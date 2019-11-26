#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
from getopt import getopt
import os
import sys
from XmindzenToTestlink import xmind_to_dict
from XmindzenToTestlink import dict_to_xml

def get_flist(fdir):
    flist = []
    for i in os.listdir(fdir):
        path = os.path.join(fdir, i)
        if os.path.isdir(path):
            flist.extend(get_flist(path))
        elif path.find('.xmind') >= 0:
            flist.append(path)
    return flist

def usage():
    '''
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
    '''
    print(usage.__doc__)

def main():
    if len(sys.argv) <= 1:
        usage()
        sys.exit()
    opts,args = getopt(sys.argv[1:],"d:t:i:ah")
    xmind_type = "case"
    xml_name = "out.xml"
    xmind_dir = "demo"
    output_dir = "output"
    is_api = False
    for k,v in opts:
        if k == "-d":
            xmind_dir = os.path.basename(v.strip("/"))
            xml_name = xmind_dir + ".xml"
            xml_path = os.path.join(output_dir, xml_name)
        if k == "-t":
            xmind_type = v
        if k == "-a":
            is_api = True
        if k == "-i":
            req_root_ID = v
        if k == "-h":
            usage()
            sys.exit()

    xmind_file_list = get_flist(xmind_dir)
    xd = xmind_to_dict.XmindToDict(xmind_type)
    dx = dict_to_xml.DictToXml()
    out = ET.Element(dx.case_tag['ts'], attrib = {"name" : xmind_dir})
    for xmind_file in xmind_file_list:
        try :
            root_dict = xd.start(xmind_file)
            if xmind_type == "case":
                root_elem = dx.get_case_xml(root_dict['suites'][0], out, api = is_api)
            elif xmind_type == "req":
                root_elem = dx.get_req_xml(root_dict['suites'][0], root_id = req_root_ID)
            print("SUCCESS \t" + xmind_file)
        except:
            print('\033[1;31mFAILED \t' + xmind_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if xmind_type == "case":
        w = ET.ElementTree(out)
        dx.indent(out)
        w.write(xml_path, 'utf-8', True)
    elif xmind_type == "req":
        w = ET.ElementTree(root_elem)
        dx.indent(root_elem)
        w.write(xml_path, 'utf-8', True)

if __name__ == "__main__":
    main()
