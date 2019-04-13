Update system packages:
  pkg.uptodate:
    - refresh: True

utils:
  pkg:
    - names
      - mc
      - htop
      - net-tools
      - dnsutils
      - mtr-tiny
      - ncdu
    - installed
    - require: [Update system packages]
