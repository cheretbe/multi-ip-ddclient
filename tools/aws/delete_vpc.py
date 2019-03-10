#!/usr/bin/env python3

import boto3
import aws_common

ec2 = boto3.resource("ec2")

print("Getting VPC ID")
vpc = aws_common.aws_vpc_by_name(ec2, "ddclient-test")
print("VPC ID: " + vpc.id)

print("Deleting VPC '{}'".format(vpc.id))
vpc.delete()