```shell
vagrant ssh-config > /tmp/vagrant-ssh-config
scp -F /tmp/vagrant-ssh-config ~/keys/aws-test-key-pair.pem default:.ssh/aws-test-key-pair.pem
```

```shell
# Query existing objects
aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test
vpc_id=$(aws ec2 describe-vpcs --filters Name=tag:Name,Values=ddclient-test --query 'Vpcs[0].VpcId' --output text)
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpc_id" --query "Subnets[*].[CidrBlock,SubnetId]"
```