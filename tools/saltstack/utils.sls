Update system packages:
  pkg.uptodate:
    - refresh: True

mc:
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
