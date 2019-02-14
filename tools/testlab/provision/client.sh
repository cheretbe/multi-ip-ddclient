#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail

if which apt-get &> /dev/null; then
  apt-get -y -q update
  apt-get -y -q upgrade
  apt-get -y -q install python3-pip git mc
elif which dnf &> /dev/null; then
  dnf -y update
  dnf -y install python3 python3-pip
elif which yum &> /dev/null; then
  yum -y update
  # yum -y install centos-release-scl
  # yum -y install rh-python36
  yum -y install epel-release
  yum -y install python36 python36-pip git mc

  # ln -fs /opt/rh/rh-python36/root/usr/bin/python3.6 /usr/bin/python3
  # ln -fs /opt/rh/rh-python36/root/usr/bin/pip3.6 /usr/bin/pip3
  ln -fs /usr/bin/python3.6 /usr/bin/python3
  ln -fs /usr/bin/pip3.6 /usr/bin/pip3
elif which zypper &> /dev/null; then
  zypper -n -q install python3 python3-pip
elif which pacman &> /dev/null; then
  pacman -Syu --noconfirm
  pacman -S --noconfirm python python-pip
else
  >&2 echo "Unsupported package manager"
  exit 1
fi

python3 --version
pip3 --version

if [ -e "/media/sf_debug/" ]; then
  usermod -a -G vboxsf vagrant
fi

exit 0
