#!/usr/bin/env python3

import argparse
import boto3

parser = argparse.ArgumentParser(description="AWS instance deletion helper")

parser.add_argument("instance_name", nargs="*", default=None,
    help="instance name to terminate")

parser.add_argument("-n", "--nowait", dest="no_wait", action="store_true",
    default=False, help="do not wait for actual instance(s) termination")

options = parser.parse_args()

ec2_client = boto3.client("ec2")

instance_filter = [{"Name": "tag:Group", "Values": ["ddclient-test"]}]
if options.instance_name:
    instance_filter += [{"Name": "tag:Name", "Values": options.instance_name}]

print("Querying instances")
response = ec2_client.describe_instances(Filters=instance_filter)
instances = [i["Instances"][0] for i in response["Reservations"]]

running_instance_ids = []
for instance in instances:
    if instance["State"]["Name"] == "running":
        print("Terminating instance '{}'".format(instance["InstanceId"]))
        ec2_client.terminate_instances(InstanceIds=[instance["InstanceId"]])
        running_instance_ids += [instance["InstanceId"]]

if (not options.no_wait) and running_instance_ids:
    print("Waiting for instance(s) to terminate...")
    waiter = ec2_client.get_waiter("instance_terminated")
    waiter.wait(InstanceIds=running_instance_ids)

print("Done")