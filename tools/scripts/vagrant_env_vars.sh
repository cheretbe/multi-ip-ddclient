#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail

grep -qxF 'source ~/custom_env_vars.sh' ~/.profile || printf "\nsource ~/custom_env_vars.sh\n" >> ~/.profile

echo "Setting custom environment variables"
echo "# Custom environment variables" > ~/custom_env_vars.sh
chmod 600 ~/custom_env_vars.sh
for env_var in ${1}; do
  echo "  ${env_var}"
  if [ -z "${!env_var}" ]; then
    >&2 echo "Environment variable '${env_var}' is not defined"
    >&2 echo "For this Vagrantfile to work correctly the following " \
      "environment variables need to be defined: ${1}"
    exit 1
  fi
  echo "export ${env_var}=${!env_var}" >>~/custom_env_vars.sh
done

exit 0
