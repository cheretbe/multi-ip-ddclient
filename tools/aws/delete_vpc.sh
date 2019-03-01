#!/bin/bash

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
# -e          Exit immediately if a command exits with a non-zero status
# -u          Treat unset variables as an error when substituting
# -o pipefail The return value of a pipeline is the status of
#             the last command to exit with a non-zero status,
#             or zero if no command exited with a non-zero status
set -euo pipefail

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

echo "Getting gateway ID"
gateway_id=$(aws ec2 describe-internet-gateways \
  --filters Name=tag:Name,Values=ddclient-test \
  --query "InternetGateways[0].InternetGatewayId" --output text)
echo Gateway ID: $gateway_id

echo "Detaching the gateway from the VPC"
aws ec2 detach-internet-gateway --internet-gateway-id $gateway_id --vpc-id $vpc_id

echo "Deleting the gateway"
aws ec2 delete-internet-gateway --internet-gateway-id $gateway_id

echo "Deleting the VPC"
aws ec2 delete-vpc --vpc-id $vpc_id