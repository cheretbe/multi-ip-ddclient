#!/usr/bin/env python3

import os
import sys
import argparse
import time
import subprocess
import boto3
import aws_common

script_dir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description="AWS instance creation helper")

parser.add_argument("-c", "--client", dest="is_client", action="store_true",
    default=False, help="create client instance")
parser.add_argument("-p", "--private-ip", dest="private_ip", default=None,
    help="Private IP address (default: 10.0.0.100 for a client, 10.0.1.11 for a router)"
)
parser.add_argument("-n", "--instance-name", dest="instance_name", default=None,
    help="Instance name (default: 'ddclient-test-client' for a client, "
        "'ddclient-test-router' for a router)"
)
parser.add_argument("-d", "--linux-distribution", default="ubuntu-xenial",
    choices=["ubuntu-xenial", "ubuntu-bionic", "rhel-6", "rhel-7", "centos-6",
        "centos-7"],
    help="Linux distribution (default: ubuntu-xenial)")
parser.add_argument("--list-ami-ids", action="store_true", default=False,
    help="list AMI ID for each Linux distribution and exit")

options = parser.parse_args()

ec2 = boto3.resource("ec2")

ami_filters_map = {
    # https://askubuntu.com/questions/53582/how-do-i-know-what-ubuntu-ami-to-launch-on-ec2/53586#53586
    "ubuntu-xenial": [
        {"Name": "name", "Values": ["ubuntu/images/hvm-ssd/ubuntu-xenial*"]},
        {"Name": "owner-id", "Values": ["099720109477"]}
    ],
    "ubuntu-bionic": [
        {"Name": "name", "Values": ["ubuntu/images/hvm-ssd/ubuntu-bionic*"]},
        {"Name": "owner-id", "Values": ["099720109477"]}
    ],
    # https://access.redhat.com/solutions/15356
    "rhel-6": [
        {"Name": "name", "Values": ["RHEL-6.?*GA*"]},
        {"Name": "owner-id", "Values": ["309956199498"]}
    ],
    "rhel-7": [
        {"Name": "name", "Values": ["RHEL-7.?*GA*"]},
        {"Name": "owner-id", "Values": ["309956199498"]}
    ],
    # https://wiki.centos.org/Cloud/AWS
    "centos-6": [
        {"Name": "product-code", "Values": ["6x5jmcajty9edm3f211pqjfn2"]}
    ],
    "centos-7": [
        {"Name": "product-code", "Values": ["aw0evgkw8e5c1q413zgy5pjce"]}
    ]
}

instance_types_map = {
    "ubuntu-xenial": "t2.micro",
    "ubuntu-bionic": "t2.micro",
    "rhel-6": "t2.micro",
    "rhel-7": "t2.micro",
    "centos-6": "t2.micro",
    "centos-7": "t2.micro"
}

user_names_map = {
    "ubuntu-xenial": "ubuntu",
    "ubuntu-bionic": "ubuntu",
    "rhel-6": "ec2-user",
    "rhel-7": "ec2-user",
    "centos-6": "centos",
    "centos-7": "centos"
}

if options.list_ami_ids:
    print("Listing AMI IDs")
    for dist, ami_filter in ami_filters_map.items():
        # print(dist, ami_filter)
        filtered_images = ec2.images.filter(Filters=ami_filter)
        image = sorted(filtered_images, key=lambda item: item.creation_date)[-1]
        print("{}: {}".format(dist, image.id))
    sys.exit(0)


if not options.is_client and (options.linux_distribution != "ubuntu-xenial"):
    raise aws_common.NoTracebackException("Only 'ubuntu-xenial' distribution "
        "is supported for router instances")

ami_filter = ami_filters_map[options.linux_distribution]
instance_type = instance_types_map[options.linux_distribution]
user_name = user_names_map[options.linux_distribution]

if options.is_client:
    print("Creating client instance")
    if not options.private_ip:
        options.private_ip = "10.0.0.100"
    security_group_name = "ddclient-test-private"
    subnet_name = "ddclient-test-private"
    if not options.instance_name:
        options.instance_name = "ddclient-test-client"

    print("Getting router instance ID")
    filtered_instances = ec2.instances.filter(Filters=[{"Name": "tag:Name",
        "Values": ["ddclient-test-router"]}])
    router_instance = next((x for x in filtered_instances if x.state["Name"] == "running"), None)
    if not router_instance:
        raise aws_common.NoTracebackException("Router instance has to be started first")
else:
    print("Creating router instance")
    if not options.private_ip:
        options.private_ip = "10.0.1.11"
    security_group_name = "ddclient-test-public"
    subnet_name = "ddclient-test-public"
    if not options.instance_name:
        options.instance_name = "ddclient-test-router"

print("Private IP: " + options.private_ip)
print("Instance name: " + options.instance_name)
print("Distribution: " + options.linux_distribution)

print("Getting image ID")
filtered_images = ec2.images.filter(Filters=ami_filter)
image = sorted(filtered_images, key=lambda item: item.creation_date)[-1]
print("Image ID: " + image.id)
print("Image name: " + image.name)

print("Security group name: " + security_group_name)
print("Getting security group ID")
security_group_filter = [{"Name": "group-name", "Values": [security_group_name]}]
security_group_id =list(ec2.security_groups.filter(Filters=security_group_filter))[0].id
print("Security group ID: " + security_group_id)

print("Subnet name: " + subnet_name)
print("Getting subnet ID")
subnet_filter = [{"Name": "tag:Name", "Values": [subnet_name]}]
subnet_id = list(ec2.subnets.filter(Filters=subnet_filter))[0].id
print("Subnet ID: " + subnet_id)

print("Instance type: " + instance_type)

print("\nRunning instance")
instance = list(ec2.create_instances(
    ImageId=image.id,
    InstanceType=instance_type,
    KeyName="test-key-pair",
    SecurityGroupIds=[security_group_id],
    SubnetId=subnet_id,
    PrivateIpAddress=options.private_ip,
    TagSpecifications=[{
        "ResourceType": "instance",
        "Tags": [
            {"Key": "Name", "Value": options.instance_name},
            {"Key": "Group", "Value": "ddclient-test"}
        ]
    }],
    MinCount=1,
    MaxCount=1
))[0]

instance.wait_until_exists()
print("Instance ID: " + instance.id)

print("Waiting for instance to start...")
instance.wait_until_running()

if not options.is_client:
    print("Disabling source/destination checking")
    instance.modify_attribute(Attribute="sourceDestCheck", Value="False")

    print("Getting private route table ID")
    route_table_filter = [{"Name": "tag:Name", "Values": ["ddclient-test-private"]}]
    route_table = list(ec2.route_tables.filter(Filters=route_table_filter))[0]
    print("Private route table ID: " + route_table.id)
    print("Adding route 0.0.0.0/0 via {} to {}".format(instance.id, route_table.id))
    route_table.create_route(DestinationCidrBlock="0.0.0.0/0",
        InstanceId=instance.id)

    print("Instance's public IP: " + instance.public_ip_address)

    aws_common.wait_for_ssh_port(ip=instance.public_ip_address)

    subprocess.check_call(("ssh", "-i", "~/.ssh/aws-test-key-pair.pem",
        "-o", "StrictHostKeyChecking=no",
        user_name + "@" + instance.public_ip_address, "uname -a"
    ))

    print("Configuring the instance")
    # Uploading 'config_router.sh'
    subprocess.check_call(("scp", "-o", "StrictHostKeyChecking=no",
        "-i", "~/.ssh/aws-test-key-pair.pem",
        os.path.join(script_dir, "config_router.sh"),
        user_name + "@" + instance.public_ip_address + ":"
    ))
    # Uploading 'wait_for_eth1_ip.sh'
    subprocess.check_call(("scp", "-i", "~/.ssh/aws-test-key-pair.pem",
        os.path.join(script_dir, "wait_for_eth1_ip.sh"),
        user_name + "@" + instance.public_ip_address + ":"
    ))
    # Running 'config_router.sh'
    subprocess.check_call(("ssh", "-i", "~/.ssh/aws-test-key-pair.pem",
        "-o", "StrictHostKeyChecking=no",
        user_name + "@" + instance.public_ip_address, "sudo /home/ubuntu/config_router.sh"
    ))

    print("\n\nConnect to the instance using the following command:")
    print("ssh -i ~/.ssh/aws-test-key-pair.pem {}@{}".format(user_name, instance.public_ip_address))
else:
    aws_common.wait_for_ssh_port(ip=router_instance.public_ip_address, port=2022)

    subprocess.check_call(("ssh", "-p", "2022", "-i", "~/.ssh/aws-test-key-pair.pem",
        "-o", "StrictHostKeyChecking=no",
        user_name + "@" + router_instance.public_ip_address, "uname -a"
    ))

    print("\n\nConnect to the instance using the following command:")
    print("ssh -p 2022 -i ~/.ssh/aws-test-key-pair.pem {}@{}".format(
        user_name, router_instance.public_ip_address)
    )