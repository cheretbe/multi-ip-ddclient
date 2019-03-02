```shell
vagrant ssh-config > /tmp/vagrant-ssh-config
scp -F /tmp/vagrant-ssh-config ~/keys/aws-test-key-pair.pem default:.ssh/aws-test-key-pair.pem
```

Launch an instance in the public subnet
```shell
# Get image ID
image_id=$(aws ec2 describe-images \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-xenial*" \
  --query "sort_by(Images, &CreationDate)[-1].ImageId" --output text)
echo image_id: $image_id
# Get security group ID
security_group_id=$(aws ec2 describe-security-groups \
  --filters Name=group-name,Values=ddclient-test-ssh-access \
  --query "SecurityGroups[0].GroupId" --output text)
echo security_group_id: $security_group_id
# Get public subnet ID
public_subnet_id=$(aws ec2 describe-subnets --filters Name=tag:Name,Values=ddclient-test-public \
  --query "Subnets[0].SubnetId" --output text)
echo public_subnet_id: $public_subnet_id

instance_id=$(aws ec2 run-instances --image-id $image_id --count 1 \
  --instance-type t2.micro --key-name test-key-pair \
  --security-group-ids $security_group_id \
  --subnet-id $public_subnet_id \
  --query "Instances[0].InstanceId" --output text)
echo instance_id: $instance_id
aws ec2 wait instance-running --instance-ids $instance_id

# Get instance's public IP address and connect to it
public_ip=$(aws ec2 describe-instances --instance-id $instance_id \
  --query "Reservations[0].Instances[0].PublicIpAddress" --output text)
echo public_ip: $public_ip
ssh -i ~/.ssh/aws-test-key-pair.pem ubuntu@$public_ip

# Stop and destroy the instance
aws ec2 terminate-instances --instance-ids $instance_id > /dev/null
aws ec2 wait instance-terminated --instance-ids $instance_id
```

```shell
# Query existing objects
aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test
vpc_id=$(aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test --query 'Vpcs[0].VpcId' --output text)
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpc_id" --query "Subnets[*].[CidrBlock,SubnetId]"
```