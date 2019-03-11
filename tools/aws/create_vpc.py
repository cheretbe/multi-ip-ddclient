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
vpc.wait_until_exists()
print("VPC ID: {}".format(vpc.id))
print("Setting VPC name to 'ddclient-test'")
vpc.create_tags(Tags=[{ "Key":"Name", "Value":"ddclient-test"}])
vpc.wait_until_available()

print("Creating public subnet 10.0.1.0/24")
public_subnet = ec2.create_subnet(CidrBlock="10.0.1.0/24", VpcId=vpc.id)
print("Subnet ID: {}".format(public_subnet.id))
print("Setting subnet name to 'ddclient-test-public'")
public_subnet.create_tags(Tags=[{ "Key":"Name", "Value":"ddclient-test-public"}])

print("Modifying the public subnet to automatically map a public IP on instance launch")
# The following won't work:
# public_subnet.map_public_ip_on_launch = True
# See https://github.com/boto/boto3/issues/276
public_subnet.meta.client.modify_subnet_attribute(SubnetId=public_subnet.id,
    MapPublicIpOnLaunch={"Value": True})

print("Creating private subnet 10.0.0.0/24")
private_subnet = ec2.create_subnet(CidrBlock="10.0.0.0/24", VpcId=vpc.id)
print("Subnet ID: {}".format(private_subnet.id))
print("Setting subnet name to 'ddclient-test-private'")
private_subnet.create_tags(Tags=[{ "Key":"Name", "Value":"ddclient-test-private"}])

print("Creating a gateway")
gateway = ec2.create_internet_gateway()
print("Setting gateway name to 'ddclient-test'")
gateway.create_tags(Tags=[{ "Key":"Name", "Value":"ddclient-test"}])

print("Attaching the gateway to the VPC")
vpc.attach_internet_gateway(InternetGatewayId=gateway.id)

print("Creating a custom route table")
public_route_table = ec2.create_route_table(VpcId=vpc.id)
print("Route table ID: {}".format(public_route_table.id))
print("Setting route table name to 'ddclient-test-public'")
public_route_table.create_tags(Tags=[{ "Key":"Name", "Value":"ddclient-test-public"}])

print("Adding a default route")
public_route_table.create_route(DestinationCidrBlock="0.0.0.0/0",
    GatewayId=gateway.id)

print("Associating the public subnet with the public route table")
public_route_table.associate_with_subnet(SubnetId=public_subnet.id)

print("Creating a custom route table")
private_route_table = ec2.create_route_table(VpcId=vpc.id)
print("Route table ID: {}".format(private_route_table.id))
print("Setting route table name to 'ddclient-test-private'")
private_route_table.create_tags(Tags=[{ "Key":"Name", "Value":"ddclient-test-private"}])

print("Associating the private subnet with the private route table")
private_route_table.associate_with_subnet(SubnetId=private_subnet.id)

# echo "Creating a security group for public subnet in the VPC"
# public_security_group_id=$(aws ec2 create-security-group \
#   --group-name ddclient-test-public \
#   --description "Security group for SSH access" \
#   --vpc-id $vpc_id --query "GroupId" --output text)
# echo Security group ID: $public_security_group_id
print("Creating a security group for public subnet in the VPC")
public_security_group = ec2.create_security_group(
    Description="Security group for public subnet",
    GroupName="ddclient-test-public",
    VpcId=vpc.id
)
print("Security group ID: {}".format(public_security_group.id))

print("Allow SSH access from anywhere")
public_security_group.authorize_ingress(
    IpPermissions=[{
        "FromPort": 22, "ToPort": 22, "IpProtocol": "TCP",
        "IpRanges": [{
            "CidrIp": "0.0.0.0/0",
            "Description": "Allow SSH from anywhere"
        }]
    }]
)

# echo "Allow access on port 2022 from anywhere"
# aws ec2 authorize-security-group-ingress --group-id $public_security_group_id \
#   --protocol tcp --port 2022 --cidr 0.0.0.0/0

# echo "Allow full access from the private network"
# aws ec2 authorize-security-group-ingress --group-id $public_security_group_id \
#   --protocol all --cidr 10.0.0.0/24
