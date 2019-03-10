#!/usr/bin/env python3

import boto3
import aws_common

ec2 = boto3.resource("ec2")

print("Creating VPC 'ddclient-test'")

print("Checking if the VPC already exists")
if aws_common.aws_vpc_by_name(ec2, "ddclient-test", must_exist=False):
    raise aws_common.NoTracebackException("VPC 'ddclient-test' already exists")

print("Creating the VPC")
vpc = ec2.create_vpc(CidrBlock="10.0.0.0/16")
print("VPC ID: {}".format(vpc.id))
print("Setting VPC name to 'ddclient-test'")
vpc.create_tags(Tags=[{ "Key":"Name", "Value":"ddclient-test"}])
