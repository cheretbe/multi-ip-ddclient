#!/bin/bash

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
# -e          Exit immediately if a command exits with a non-zero status
# -u          Treat unset variables as an error when substituting
# -o pipefail The return value of a pipeline is the status of
#             the last command to exit with a non-zero status,
#             or zero if no command exited with a non-zero status
set -euo pipefail

echo "Getting public security group ID"
security_group_id=$(aws ec2 describe-security-groups \
  --filters Name=group-name,Values=ddclient-test-ssh-access \
  --query "SecurityGroups[0].GroupId" --output text)
echo "Deleting security group $security_group_id"
aws ec2 delete-security-group --group-id $security_group_id

echo "Getting private security group ID"
private_security_group_id=$(aws ec2 describe-security-groups \
  --filters Name=group-name,Values=ddclient-test-private \
  --query "SecurityGroups[0].GroupId" --output text)
echo "Deleting security group $private_security_group_id"
aws ec2 delete-security-group --group-id $private_security_group_id

echo "Getting VPC ID"
vpc_id=$(aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test \
  --query "Vpcs[0].VpcId" --output text)
echo VPC ID: $vpc_id

echo "Reading subnets"
subnet_ids=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpc_id" \
  --query "Subnets[*].SubnetId" --output text)
for subnet_id in $subnet_ids; do
  echo Deleting subnet $subnet_id
  aws ec2 delete-subnet --subnet-id=$subnet_id
done

echo "Getting public route table ID"
public_route_table_id=$(aws ec2 describe-route-tables \
  --filters Name=tag:Name,Values=ddclient-test-public \
  --query "RouteTables[0].RouteTableId" --output text)
echo "Deleting route table $public_route_table_id"
aws ec2 delete-route-table --route-table-id $public_route_table_id

echo "Getting private route table ID"
private_route_table_id=$(aws ec2 describe-route-tables \
  --filters Name=tag:Name,Values=ddclient-test-private \
  --query "RouteTables[0].RouteTableId" --output text)
echo "Deleting route table $private_route_table_id"
aws ec2 delete-route-table --route-table-id $private_route_table_id

echo "Getting Internet gateway ID"
gateway_id=$(aws ec2 describe-internet-gateways --filters Name=tag:Name,Values=ddclient-test \
  --query "InternetGateways[0].InternetGatewayId" --output text)
echo Gateway ID: $gateway_id

echo "Detaching the Internet gateway from the VPC"
aws ec2 detach-internet-gateway --internet-gateway-id $gateway_id --vpc-id $vpc_id

echo "Deleting the Internet gateway"
aws ec2 delete-internet-gateway --internet-gateway-id $gateway_id

echo "Deleting the VPC"
aws ec2 delete-vpc --vpc-id $vpc_id