#!/usr/bin/env python3

import argparse
import boto3
import aws_common

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
instance = ec2.create_instances(
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
)
# instance = ec2.Instance("i-0964d17619ce858a9")

instance.wait_until_exists()
print("Instance ID: " + instance.id)

if not options.is_client:
    print("Disabling source/destination checking")
    instance.modify_attribute(Attribute="sourceDestCheck", Value="False")

print("Waiting for instance to start")
instance.wait_until_running()