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
parser.add_argument("-d", "--linux-distribution", default="ubuntu",
    choices=["ubuntu", "centos"], help="Linux distribution (default: ubuntu)")

options = parser.parse_args()

ec2 = boto3.resource("ec2")

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