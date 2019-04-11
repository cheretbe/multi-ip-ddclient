#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail

# if [ -e "/media/sf_multi-ip-ddclient/" ]; then
if [ $(getent group vboxsf) ]; then
  usermod -a -G vboxsf vagrant
fi

exit 0