#!/usr/bin/env python3

import sys
import boto3
import aws_common

ec2 = boto3.resource("ec2")

print("Getting VPC ID")
vpc = aws_common.aws_vpc_by_name(ec2, "ddclient-test")
print("VPC ID: " + vpc.id)

print("Reading security groups")
security_group_filter = [{"Name": "group-name",
    "Values": ["ddclient-test-public", "ddclient-test-private"]}]
for security_group in ec2.security_groups.filter(Filters=security_group_filter):
    print("Deleting security group '{}'".format(security_group.id))
    security_group.delete()

print("Reading subnets")
subnet_filter = [{"Name": "vpc-id", "Values": [vpc.id]}]
for subnet in ec2.subnets.filter(Filters=subnet_filter):
    print("Deleting subnet '{}'".format(subnet.id))
    subnet.delete()

print("Reading route tables")
route_table_filter = [{"Name": "tag:Name",
    "Values": ["ddclient-test-public", "ddclient-test-private"]}]
for route_table in ec2.route_tables.filter(Filters=route_table_filter):
    print("Deleting route table '{}'".format(route_table.id))
    route_table.delete()

print("Reading internet gateways")
gateway_filter = [{"Name": "attachment.vpc-id", "Values": [vpc.id]}]
for gateway in ec2.internet_gateways.filter(Filters=gateway_filter):
    print("Detaching internet gateway '{}' from VPC '{}'".format(gateway.id, vpc.id))
    gateway.detach_from_vpc(VpcId=vpc.id)
    print("Deleting internet gateway '{}'".format(gateway.id))
    gateway.delete()

print("Deleting VPC '{}'".format(vpc.id))
vpc.delete()