#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail

if which apt-get &> /dev/null; then
  apt-get -y -q update
  apt-get -y -q upgrade
  apt-get -y -q install python3-pip
elif which yum &> /dev/null; then
  yum -y update
else
  >&2 echo "Unsupported package manager"
  exit 1
fi

pip3 --version

exit 0