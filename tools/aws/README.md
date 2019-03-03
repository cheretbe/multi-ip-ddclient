```shell
vagrant ssh-config > /tmp/vagrant-ssh-config
scp -F /tmp/vagrant-ssh-config ~/keys/aws-test-key-pair.pem default:.ssh/aws-test-key-pair.pem
```

```shell
# Create VPC
/media/sf_debug/multi-ip-ddclient/tools/aws/create_vpc.sh

# Run instance
/media/sf_debug/multi-ip-ddclient/tools/aws/run_instance.sh
/media/sf_debug/multi-ip-ddclient/tools/aws/run_instance.sh -i "ubuntu/images/hvm-ssd/ubuntu-bionic*"

# Terminate instances
/media/sf_debug/multi-ip-ddclient/tools/aws/terminate_instances.sh

# Delete VPC
/media/sf_debug/multi-ip-ddclient/tools/aws/delete_vpc.sh

# Query existing objects
aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test
vpc_id=$(aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test --query 'Vpcs[0].VpcId' --output text)
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpc_id" --query "Subnets[*].[CidrBlock,SubnetId]"
```