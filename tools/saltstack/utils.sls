Update system packages:
  pkg.uptodate:
    - refresh: True

{% if grains['os'] in ['CentOS', 'RedHat'] %}
  {% set packages_to_install = ['mc', 'htop', 'net-tools', 'bind-utils',
    'mtr', 'ncdu', 'wget', 'git'] %}
{% else %}
  {% set packages_to_install = ['mc', 'htop', 'net-tools', 'dnsutils',
    'mtr-tiny', 'ncdu', 'wget', 'git'] %}
{% endif %}

utils:
  pkg:
    - names: {{ packages_to_install }}
    - installed
    - require: [Update system packages]