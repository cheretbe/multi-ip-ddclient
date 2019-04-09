#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail

grep -qxF 'source ~/custom_env_vars.sh' ~/.bashrc || printf "\nsource ~/custom_env_vars.sh\n" >> ~/.bashrc

echo "Setting custom environment variables"
echo "# Custom env variables" > ~/custom_env_vars.sh
for env_var in ${1}; do
  echo "  ${env_var}"
  echo "export ${env_var}=${!env_var}" >>~/custom_env_vars.sh
done

exit 0
