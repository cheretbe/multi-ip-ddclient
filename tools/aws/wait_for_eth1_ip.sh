#!/bin/bash

function get_eth1_ip()
{
  if [ -e "/sys/class/net/eth1" ]; then
    ip addr list eth1 |grep "inet " |cut -d' ' -f6|cut -d/ -f1
  else
    echo ""
  fi
}

echo "Waiting for 'eth1' interface IP address"
attempt=1
while (( $attempt <= 30 ))
do
  ip_addr=$(get_eth1_ip)
  if [ ! "${ip_addr}" == "" ]; then
    printf "\neth1 IP address: ${ip_addr}"
    break
  fi
  printf "."
  sleep 1
  ((attempt+=1))
done
printf "\n"