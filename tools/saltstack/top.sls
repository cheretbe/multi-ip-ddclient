#file_roots:
#  base:
#    - /srv/salt/base
#  qa:
#    - /srv/salt/aws_cli

base:
  '*':
    - webserver
awscli:
  'aws-cli':
    - test
