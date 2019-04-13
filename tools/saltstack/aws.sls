include: [python3]

Python2 PIP:
  pkg:
    - installed
    - name: python-pip

AWS CLI and Boto3:
  pip.installed:
    - names: [awscli, boto3]
    - name: awscli
    - bin_env: '/usr/bin/pip3'
    - require:
      - sls: python3
      # Without Python2 PIP installed "pip.installed" fails even if "bin_env"
      # for Python3 PIP is specified
      - pkg: Python2 PIP