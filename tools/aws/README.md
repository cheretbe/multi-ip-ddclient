```shell
vagrant ssh-config > /tmp/vagrant-ssh-config
scp -F /tmp/vagrant-ssh-config ~/keys/aws-test-key-pair.pem default:.ssh/aws-test-key-pair.pem
```

```shell
# Query existing objects
aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test
vpc_id=$(aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test --query 'Vpcs[0].VpcId' --output text)
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpc_id" --query "Subnets[*].[CidrBlock,SubnetId]"




# Create a custom route table for the VPC
route_table_id=$(aws ec2 create-route-table --vpc-id $vpc_id --query 'RouteTable.RouteTableId' --output text)
echo $route_table_id

# Create a default route in the route table
aws ec2 create-route --route-table-id $route_table_id --destination-cidr-block 0.0.0.0/0 --gateway-id $gateway_id

# Associate the public subnet with the route table
aws ec2 associate-route-table --subnet-id $public_subnet_id --route-table-id $route_table_id

# Modify the public subnet so that an instance launched into the subnet automatically receives a public IP address
aws ec2 modify-subnet-attribute --subnet-id $public_subnet_id --map-public-ip-on-launch

# Create a security group in the VPC
security_group_id=$(aws ec2 create-security-group --group-name ddclient-test-ssh-access --description "Security group for SSH access" --vpc-id $vpc_id --query "GroupId" --output text)
echo $security_group_id

# Add a rule that allows SSH access from anywhere to the security group
aws ec2 authorize-security-group-ingress --group-id $security_group_id --protocol tcp --port 22 --cidr 0.0.0.0/0

# Launch an instance in the public subnet
imageId=$(aws ec2 describe-images --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-xenial*" --query "sort_by(Images, &CreationDate)[-1].ImageId" --output text)

instance_id=$(aws ec2 run-instances --image-id $imageId --count 1 --instance-type t2.micro --key-name test-key-pair --security-group-ids $security_group_id --subnet-id $public_subnet_id --query 'Instances[0].InstanceId' --output text)
echo $instance_id
aws ec2 wait instance-running --instance-ids $instance_id

# Get instance's public IP address and connect to it
public_ip=$(aws ec2 describe-instances --instance-id $instance_id --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo $public_ip
ssh -i ~/.ssh/test-key-pair.pem ubuntu@$public_ip

# === Delete objects ===

# Stop and destroy the instance
aws ec2 terminate-instances --instance-ids $instance_id
aws ec2 wait instance-terminated --instance-ids $instance_id

# Delete the security group
security_group_id=$(aws ec2 describe-security-groups --filters Name=group-name,Values=ddclient-test-ssh-access --query "SecurityGroups[0].GroupId" --output text)
aws ec2 delete-security-group --group-id $security_group_id
```