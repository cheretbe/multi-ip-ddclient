#!/usr/bin/env python3

import sys
import time
import subprocess
import boto3
import aws_common

ec2 = boto3.resource("ec2")

print("Querying router instance")
instances = ec2.instances.filter(
    Filters=[{"Name": "tag:Name", "Values": ["ddclient-test-router"]}]
)
router_instance = next(iter([i for i in instances if i.state["Name"] == "running"]), None)

if not router_instance:
    raise aws_common.NoTracebackException("Router instance must be running")

print("Querying network interfaces")
interface_to_detach = None
interface_name_to_attach = "ddclient-test-1"
for interface in router_instance.network_interfaces:
    if interface.description == "ddclient-test-1":
        interface_to_detach = interface
        interface_name_to_attach = "ddclient-test-2"
    elif interface.description == "ddclient-test-2":
        interface_to_detach = interface
        interface_name_to_attach = "ddclient-test-1"

if interface_to_detach:
    print("Detaching network interface '{}'".format(interface_to_detach.description))
    interface_to_detach.detach()
    print("Waiting for the interface to detach")
    for i in range(30):
        interface_to_detach.reload()
        sys.stdout.write(".")
        sys.stdout.flush()
        # attachment property is None for a detached interface
        if not interface_to_detach.attachment:
            break
        time.sleep(1)
    sys.stdout.write("\nDetached\n")

print("Attaching '{}' to '{}'".format(interface_name_to_attach, router_instance.id))
interfaces = ec2.network_interfaces.filter(
    Filters=[{"Name": "description", "Values": [interface_name_to_attach]}]
)
interface_to_attach = next(iter(interfaces), None)
print("Interface ID: " + interface_to_attach.id)
interface_to_attach.attach(InstanceId=router_instance.id, DeviceIndex=1)

subprocess.check_call(("ssh", "-i", "~/.ssh/aws-test-key-pair.pem",
    "ubuntu@{}".format(router_instance.public_ip_address), "./wait_for_eth1_ip.sh"))

print("Done")