#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail

if which apt-get &> /dev/null; then
  apt-get -y -q update
  apt-get -y -q upgrade
  apt-get -y -q install python3-pip
  PIP3_PATH=$(which pip3)
elif which yum &> /dev/null; then
  yum -y update
  # yum -y install epel-release
  # localinstall doesn't return error code if the package is already installed
  yum localinstall -y https://centos7.iuscommunity.org/ius-release.rpm
  yum install -y python36u python36u-pip
  #yum -y install python-pip
  PIP3_PATH=$(which pip3.6)
elif which zypper &> /dev/null; then
  zypper -n -q install python3 python3-pip
  PIP3_PATH=$(which pip3)
else
  >&2 echo "Unsupported package manager"
  exit 1
fi

${PIP3_PATH} --version

exit 0