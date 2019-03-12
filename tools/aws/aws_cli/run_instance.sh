#!/bin/bash

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
# -e          Exit immediately if a command exits with a non-zero status
# -u          Treat unset variables as an error when substituting
# -o pipefail The return value of a pipeline is the status of
#             the last command to exit with a non-zero status,
#             or zero if no command exited with a non-zero status
set -euo pipefail

script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
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
  subnet_name="ddclient-test-private"
  instance_name="ddclient-test-client"

  echo "Getting router instance ID"
  router_instance_id=$(aws ec2 describe-instances \
    --filters Name=tag:Name,Values=ddclient-test-router \
    --query "Reservations[*].Instances[?State.Name=='running'].InstanceId" \
    --output text)
  if [ "${router_instance_id}" == "" ] ; then
    echo "ERROR: Router instance has to be started first" 1>&2
    exit 1
  fi
  echo "Router instance ID: ${router_instance_id}"
else
  echo "Creating router instance"
  private_ip="10.0.1.11"
  security_group_name="ddclient-test-public"
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

  set +e
  echo "Waiting for SSH to become avialable..."
  attempt=1
  maxConnectionAttempts=5
  sleepSeconds=5
  while (( $attempt <= $maxConnectionAttempts ))
  do
    ssh -o StrictHostKeyChecking=no -i ~/.ssh/aws-test-key-pair.pem ubuntu@${public_ip} 'ls ~ >/dev/null'
    case $? in
      (0) echo "SSH is available"; break ;;
      (*) echo "Attempt ${attempt} of ${maxConnectionAttempts}: SSH is not available, waiting ${sleepSeconds} seconds..." ;;
    esac
    sleep $sleepSeconds
    ((attempt+=1))
  done
  set -e

  echo "Configuring the instance"
  scp -o StrictHostKeyChecking=no -i ~/.ssh/aws-test-key-pair.pem ${script_path}/config_router.sh ubuntu@${public_ip}:
  ssh -i ~/.ssh/aws-test-key-pair.pem ubuntu@${public_ip} sudo /home/ubuntu/config_router.sh

  printf "\n\nConnect to the instance with the following command:\n"
  echo "ssh -i ~/.ssh/aws-test-key-pair.pem ubuntu@${public_ip}"
else
  echo "Getting private route table ID"
  private_route_table_id=$(aws ec2 describe-route-tables \
    --filters Name=tag:Name,Values=ddclient-test-private \
    --query "RouteTables[0].RouteTableId" --output text)
  echo "Adding 0.0.0.0/0 route to ${private_route_table_id} via ${router_instance_id}"
  aws ec2 create-route --route-table-id ${private_route_table_id} \
    --destination-cidr-block 0.0.0.0/0 --instance-id ${router_instance_id} > /dev/null

  echo "Getting router public IP"
  public_ip=$(aws ec2 describe-instances --instance-id $router_instance_id \
    --query "Reservations[0].Instances[0].PublicIpAddress" --output text)
  echo Router IP: $public_ip

  printf "\n\nConnect to the instance with the following command:\n"
  echo "ssh -p 2022 -i ~/.ssh/aws-test-key-pair.pem ubuntu@${public_ip}"
fi