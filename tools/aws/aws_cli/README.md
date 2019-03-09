Old proof-of-concept code, that uses AWS CLI. Replaced with Python script in
parent directory.

```shell
vagrant ssh-config > /tmp/vagrant-ssh-config
scp -F /tmp/vagrant-ssh-config ~/keys/aws-test-key-pair.pem default:.ssh/aws-test-key-pair.pem
# Windows
vagrant ssh-config > %TEMP%\vagrant-ssh-config
scp -F %TEMP%\vagrant-ssh-config %USERPROFILE%\keys\aws-test-key-pair.pem default:.ssh/aws-test-key-pair.pem
DEL %TEMP%\vagrant-ssh-config
```

```shell
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables --table nat --append POSTROUTING -s 10.0.0.0/24 --out-interface eth0 -j MASQUERADE
iptables --table nat --append PREROUTING --in-interface eth0 \
  --protocol tcp --dport 2022 -j DNAT --to 10.0.0.100:22
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