#!/usr/bin/env python3

import os
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
    choices=["ubuntu-xenial", "ubuntu-bionic", "centos-7"],
    help="Linux distribution (default: ubuntu-xenial)")

options = parser.parse_args()

ec2 = boto3.resource("ec2")

ami_names_map = {
    "ubuntu-xenial": "ubuntu/images/hvm-ssd/ubuntu-xenial*",
    "ubuntu-bionic": "ubuntu/images/hvm-ssd/ubuntu-bionic*",
    "centos-7": ""}
image_name = ami_names_map[options.linux_distribution]

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
print("Image name: " + image_name)

print("Getting image ID")
filtered_images = ec2.images.filter(Filters=[{"Name": "name", "Values": [image_name]}])
image_id = sorted(filtered_images, key=lambda item: item.creation_date)[-1].id
print("Image ID: " + image_id)

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

print("\nRunning instance")
instance = list(ec2.create_instances(
    ImageId=image_id,
    InstanceType="t2.nano",
    KeyName="test-key-pair",
    SecurityGroupIds=[security_group_id],
    SubnetId=subnet_id,
    PrivateIpAddress=options.private_ip,
    TagSpecifications=[{
        "ResourceType": "instance",
        "Tags": [{"Key": "Name", "Value": options.instance_name}]
    }],
    MinCount=1,
    MaxCount=1
))[0]

instance.wait_until_exists()
print("Instance ID: " + instance.id)

if not options.is_client:
    print("Disabling source/destination checking")
    instance.modify_attribute(Attribute="sourceDestCheck", Value="False")

print("Waiting for instance to start...")
instance.wait_until_running()

if not options.is_client:
    print("Instance's public IP: " + instance.public_ip_address)
    print("Waiting for SSH to become avialable...")
    retry_count = 5
    sleep_time = 5
    for i in range(retry_count):
        if aws_common.port_is_open(instance.public_ip_address, 22):
            print("Port 22 is open")
            break
        else:
            print("[{}/{}] Port 22 is not available. Sleeping for {} seconds".format(
                i + 1, retry_count, sleep_time)
            )
            time.sleep(sleep_time)
    subprocess.check_call(("ssh", "-i", "~/.ssh/aws-test-key-pair.pem",
        "-o", "StrictHostKeyChecking=no",
        "ubuntu@" + instance.public_ip_address, "uname -a"
    ))

    print("Configuring the instance")
    subprocess.check_call(("scp", "-o", "StrictHostKeyChecking=no",
        "-i", "~/.ssh/aws-test-key-pair.pem",
        os.path.join(script_dir, "config_router.sh"),
        "ubuntu@" + instance.public_ip_address + ":"
    ))
    subprocess.check_call(("ssh", "-i", "~/.ssh/aws-test-key-pair.pem",
        "-o", "StrictHostKeyChecking=no",
        "ubuntu@" + instance.public_ip_address, "sudo /home/ubuntu/config_router.sh"
    ))

    print("\n\nConnect to the instance using the following command:")
    print("ssh -i ~/.ssh/aws-test-key-pair.pem ubuntu@{}".format(instance.public_ip_address))
else:
    print("Getting private route table ID")
    route_table_filter = [{"Name": "tag:Name", "Values": ["ddclient-test-private"]}]
    route_table = list(ec2.route_tables.filter(Filters=route_table_filter))[0]
    print("Private route table ID: " + route_table.id)
    print("Adding route 0.0.0.0/0 via {} to {}".format(router_instance.id, route_table.id))
    route_table.create_route(DestinationCidrBlock="0.0.0.0/0",
        InstanceId=router_instance.id)

    print("\n\nConnect to the instance using the following command:")
    print("ssh -p 2022 -i ~/.ssh/aws-test-key-pair.pem ubuntu@{}".format(
        router_instance.public_ip_address)
    )