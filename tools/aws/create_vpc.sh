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

echo "Creating subnet 10.0.1.0/24"
public_subnet_id=$(aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.1.0/24 \
  --query "Subnet.SubnetId" --output text)
echo Subnet ID: $public_subnet_id
echo "Setting subnet name to 'ddclient-test-public'"
aws ec2 create-tags --resources $public_subnet_id --tags Key=Name,Value="ddclient-test-public"

echo "Creating subnet 10.0.0.0/24"
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
