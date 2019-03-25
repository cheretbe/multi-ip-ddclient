This directory contains scripts that manage testing infrastructure in Amazon
VPC.

### Contents

* [Overview](#overview)
* [Notes](#notes)
* [Usage Examples](#usage-examples)
* [Useful Links](#useful-links)

### Overview

Network diagram for the VPC

![network_diagram](images/aws_vpc_diagram.png)

### Notes

This VPC is used solely for the purpose of testing multi-ip-ddclient in different
operating systems. It should not be used in a production environment.

* It has relaxed security: ssh ports accessible from anywhere both
for public and private subnets, default user names are used.
* Secondary network interface is not usable. It is present only to emulate
IP address change.
* :warning: External IP address is lost on 'ddclient-test-router' instance
restart. After that the VPC becomes inaccessible from the outside.

### Usage Examples

```ssh
./create_vpc.py
./run_instance.py
./run_instance.py -c
./execute_on_client.py script_that_expects_eth1_to_fail.sh
./change_eth1_ip.py
./execute_on_client.py script_that_expects_first_ip_on_eth1.sh
./change_eth1_ip.py
./execute_on_client.py script_that_expects_second_ip_on_eth1.sh
./terminate_instances.py
./delete_vpc.py
```

### Useful Links

* https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html
* https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Scenarios.html
* https://aws.amazon.com/premiumsupport/knowledge-center/ec2-centos-rhel-secondary-interface/