# XmindzenToTestlink

Usgae:

  生成用例xml:
    xmindzen2testlink -d xmind文件目录 -t case -a  #加-a 生成api用例, 不加a为其他用例
  生成需求xml:
    xmindzen2testlink -d xmind文件目录 -t req -i 需求的ID标识

  args:
    -d dir
    -t req/case
    -a api_or_not
    -i req_root_id
    -h help

env:
    XMind Zen
    python3

the mapping relations:
    ...to be continued
