#!/bin/bash

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
# -e          Exit immediately if a command exits with a non-zero status
# -u          Treat unset variables as an error when substituting
# -o pipefail The return value of a pipeline is the status of
#             the last command to exit with a non-zero status,
#             or zero if no command exited with a non-zero status
set -euo pipefail

ids_to_wait=()
echo "Querying instances"

instance_ids=$(aws ec2 describe-instances \
  --filters Name=tag:Name,Values=ddclient-test-client,ddclient-test-router \
  --query "Reservations[*].Instances[?State.Name!='terminated'].InstanceId" \
  --output text)
for instance_id in $instance_ids; do
  echo Terminating instance $instance_id
  aws ec2 terminate-instances --instance-ids $instance_id > /dev/null
  ids_to_wait+=($instance_id)
done

if [ ${#ids_to_wait[@]} -ne 0 ]; then
  echo "Waiting for instance(s) to terminate"
  aws ec2 wait instance-terminated --instance-ids "${ids_to_wait[@]}"
fi

echo "Done"