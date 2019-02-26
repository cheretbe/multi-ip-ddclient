```shell
# Query existing objects
aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test
vpc_id=$(aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test --query 'Vpcs[0].VpcId' --output text)
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpc_id" --query "Subnets[*].[CidrBlock,SubnetId]"

# Create a VPC
vpc_id=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text)
echo $vpc_id

# Name the VPC
aws ec2 create-tags --resources "$vpc_id" --tags Key=Name,Value="ddclient-test"

# Create subnets
aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.1.0/24
aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.0.0/24

# Delete objects
vpc_id=$(aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test --query 'Vpcs[0].VpcId' --output text)
for i in `aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpc_id" --query "Subnets[*].SubnetId" --output text`; do echo Deleting subnet $i; aws ec2 delete-subnet --subnet-id=$i; done
aws ec2 delete-vpc --vpc-id $vpc_id
```