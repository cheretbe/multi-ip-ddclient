#!/bin/bash

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
# -e          Exit immediately if a command exits with a non-zero status
# -u          Treat unset variables as an error when substituting
# -o pipefail The return value of a pipeline is the status of
#             the last command to exit with a non-zero status,
#             or zero if no command exited with a non-zero status
set -euo pipefail

echo "Checking if VPC already exists"
existing_vpc_id=$(aws ec2 describe-vpcs \
  --filters Name=tag:Name,Values=ddclient-test \
  --query "Vpcs[0].VpcId" --output text)
if [ $existing_vpc_id != "None" ] ; then
  echo "ERROR: VPC named 'ddclient-test' already exists. Use delete_vpc.sh to delete"
  exit 1
fi

echo "Creating a VPC"
vpc_id=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query "Vpc.VpcId" --output text)
echo VPC ID: $vpc_id
echo "Setting VPC name to 'ddclient-test'"
aws ec2 create-tags --resources "$vpc_id" --tags Key=Name,Value="ddclient-test"

echo "Creating public subnet 10.0.1.0/24"
public_subnet_id=$(aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.1.0/24 \
  --query "Subnet.SubnetId" --output text)
echo Subnet ID: $public_subnet_id
echo "Setting subnet name to 'ddclient-test-public'"
aws ec2 create-tags --resources $public_subnet_id --tags Key=Name,Value="ddclient-test-public"

echo "Modifying the public subnet to automatically map a public IP on instance launch"
aws ec2 modify-subnet-attribute --subnet-id $public_subnet_id --map-public-ip-on-launch

echo "Creating private subnet 10.0.0.0/24"
private_subnet_id=$(aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.0.0/24 \
  --query Subnet.SubnetId --output text)
echo Subnet ID: $private_subnet_id
echo "Setting subnet name to 'ddclient-test-private'"
aws ec2 create-tags --resources $private_subnet_id --tags Key=Name,Value="ddclient-test-private"

echo "Creating a gateway"
gateway_id=$(aws ec2 create-internet-gateway --query "InternetGateway.InternetGatewayId" --output text)
echo Gateway ID: $gateway_id
echo "Setting gateway name to 'ddclient-test'"
aws ec2 create-tags --resources $gateway_id --tags Key=Name,Value="ddclient-test"

echo "Attaching the gateway to the VPC"
aws ec2 attach-internet-gateway --vpc-id $vpc_id --internet-gateway-id $gateway_id

echo "Creating a custom route table for the VPC"
public_route_table_id=$(aws ec2 create-route-table --vpc-id $vpc_id --query \
  "RouteTable.RouteTableId" --output text)
echo Route table ID: $public_route_table_id
echo "Setting route table name to 'ddclient-test-public'"
aws ec2 create-tags --resources $public_route_table_id \
  --tags Key=Name,Value="ddclient-test-public"

echo "Adding a default route"
aws ec2 create-route --route-table-id $public_route_table_id \
  --destination-cidr-block 0.0.0.0/0 --gateway-id $gateway_id > /dev/null

echo "Associating the public subnet with the public route table"
aws ec2 associate-route-table --subnet-id $public_subnet_id \
  --route-table-id $public_route_table_id > /dev/null

echo "Creating a security group for SSH access in the VPC"
security_group_id=$(aws ec2 create-security-group --group-name ddclient-test-ssh-access \
  --description "Security group for SSH access" \
  --vpc-id $vpc_id --query "GroupId" --output text)
echo Security group ID: $security_group_id

echo "Adding a rule that allows SSH access from anywhere"
aws ec2 authorize-security-group-ingress --group-id $security_group_id \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

echo "Creating a custom route table for the VPC"
private_route_table_id=$(aws ec2 create-route-table --vpc-id $vpc_id --query \
  "RouteTable.RouteTableId" --output text)
echo Route table ID: $private_route_table_id
echo "Setting route table name to 'ddclient-test-private'"
aws ec2 create-tags --resources $private_route_table_id \
  --tags Key=Name,Value="ddclient-test-private"

echo "Creating a security group for private subnet in the VPC"
private_security_group_id=$(aws ec2 create-security-group --group-name ddclient-test-private \
  --description "Security group for private subnet" \
  --vpc-id $vpc_id --query "GroupId" --output text)
echo Security group ID: $private_security_group_id

echo "Adding a rule that allows SSH access from the public subnet"
aws ec2 authorize-security-group-ingress --group-id $private_security_group_id \
  --protocol tcp --port 22 --cidr 10.0.1.0/24