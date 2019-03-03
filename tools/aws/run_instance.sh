#!/bin/bash

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
# -e          Exit immediately if a command exits with a non-zero status
# -u          Treat unset variables as an error when substituting
# -o pipefail The return value of a pipeline is the status of
#             the last command to exit with a non-zero status,
#             or zero if no command exited with a non-zero status
set -euo pipefail

is_client=0
image_name="ubuntu/images/hvm-ssd/ubuntu-xenial*"

# parse options
while getopts ":i:hc" opt; do
  case $opt in
    h) echo "run_instance.sh [-h] [-c] [-i] IMAGE_NAME"; exit;;
    c) is_client=1 ;;
    i) image_name="$OPTARG" ;;
    \?) echo "Invalid option: -$OPTARG" >&2 ; exit 1;;
  esac
done

# shift to get access to positional arguments
shift "$((OPTIND-1))"

if [ $is_client -eq 1 ]; then
  echo "Creating client instance"
  private_ip="10.0.0.100"
  security_group_name="ddclient-test-private"
  subnet_name="ddclient-test-public"
  instance_name="ddclient-test-client"
else
  echo "Creating router instance"
  private_ip="10.0.1.11"
  security_group_name="ddclient-test-ssh-access"
  subnet_name="ddclient-test-public"
  instance_name="ddclient-test-router"
fi

echo Image name: $image_name
# Get image ID
image_id=$(aws ec2 describe-images \
  --filters "Name=name,Values=${image_name}" \
  --query "sort_by(Images, &CreationDate)[-1].ImageId" --output text)
echo Image ID: $image_id

echo Security group name: $security_group_name
# Get security group ID
security_group_id=$(aws ec2 describe-security-groups \
  --filters Name=group-name,Values=${security_group_name} \
  --query "SecurityGroups[0].GroupId" --output text)
echo Security group ID: $security_group_id

echo Subnet name: $subnet_name
# Get subnet ID
subnet_id=$(aws ec2 describe-subnets --filters Name=tag:Name,Values=${subnet_name} \
  --query "Subnets[0].SubnetId" --output text)
echo Subnet ID: $subnet_id

# t2.micro
echo Running instance \'${instance_name}\' with private IP address: $private_ip
instance_id=$(aws ec2 run-instances --count 1 \
  --image-id $image_id \
  --instance-type t2.nano \
  --key-name test-key-pair \
  --security-group-ids $security_group_id \
  --subnet-id $subnet_id \
  --private-ip-address $private_ip \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${instance_name}}]" \
  --query "Instances[0].InstanceId" --output text)
echo Instance ID: $instance_id

if [ $is_client -eq 0 ]; then
  echo "Disabling source/destination checking"
  aws ec2 modify-instance-attribute --instance-id $instance_id --no-source-dest-check
fi

echo "Waiting for instance to start"
aws ec2 wait instance-running --instance-ids $instance_id

if [ $is_client -eq 0 ]; then
  echo "Getting instance's public IP"
  public_ip=$(aws ec2 describe-instances --instance-id $instance_id \
    --query "Reservations[0].Instances[0].PublicIpAddress" --output text)
  echo Public IP: $public_ip

  printf "\n\nConnect to the instance with the following command:\n"
  echo "ssh -i ~/.ssh/aws-test-key-pair.pem ubuntu@${public_ip}"
fi