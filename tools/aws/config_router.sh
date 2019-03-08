#!/bin/bash

# http://redsymbol.net/articles/unofficial-bash-strict-mode/
# -e          Exit immediately if a command exits with a non-zero status
# -u          Treat unset variables as an error when substituting
# -o pipefail The return value of a pipeline is the status of
#             the last command to exit with a non-zero status,
#             or zero if no command exited with a non-zero status
set -euo pipefail

echo "Enabling IP forwarding"
sed -i 's/#net.ipv4.ip_forward/net.ipv4.ip_forward/g' /etc/sysctl.conf
sed -i '/^net.ipv4.ip_forward.*/s/^net.ipv4.ip_forward.*/net.ipv4.ip_forward = 1/g' /etc/sysctl.conf
sysctl -p /etc/sysctl.conf

echo "Adding NAT/DNAT rules"
iptables --table nat --append POSTROUTING -s 10.0.0.0/24 \
  --out-interface eth0 -j MASQUERADE
iptables --table nat --append PREROUTING --in-interface eth0 \
  --protocol tcp --dport 2022 -j DNAT --to 10.0.0.100:22

