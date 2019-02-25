```shell
aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test

# Create a VPC
vpc_id=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text)
echo $vpc_id

# Name the VPC
aws ec2 create-tags --resources "$vpc_id" --tags Key=Name,Value="ddclient-test"

# Create subnets
aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.1.0/24
aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.0.0/24
```