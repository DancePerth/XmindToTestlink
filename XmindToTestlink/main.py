#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
import os
import sys
import argparse
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

def save_xml(dx, xml_out, xml_path):
    w = ET.ElementTree(xml_out)
    #dx.indent(xml_out)
    w.write(xml_path, 'utf-8', True)

def run(xmind_file_list, xmind_type, is_api, xmind_msg, xd, dx, output_dir, \
        need_req, need_case, single_create, auto_id, root_id, name):
    if single_create:
        #加-s: 单个文件生成需求和用例xml(不常用,待商榷)
        for xmind_file in xmind_file_list:
            file_msg = os.path.basename(xmind_file).split('.')[0]
            xml_name = file_msg + ".xml"
            xml_req_name =  file_msg + "_req.xml"
            xml_path = os.path.join(output_dir, xml_name)
            xml_req_path = os.path.join(output_dir, xml_req_name)
            try:
                out = ET.Element(dx.case_tag['ts'], attrib = {"name" : file_msg})
                req_out = ET.Element(dx.req_tag['root'])
                root_dict, req_dict = xd.start(xmind_file)
                if need_case:
                    dx.get_case_xml(root_dict['suites'][0], out, api = is_api)
                    save_xml(dx, out, xml_path)
                if need_req:
                    dx.get_req_xml(req_dict['suites'][0], req_out, auto_id, root_id)
                    save_xml(dx, req_out, xml_req_path)
                print("SUCCESS \t" + xmind_file)
            except Exception as e:
                print(e)
                print('\033[1;31mFAILED \t%s\033[m'%xmind_file)
    else:
        #不加-s: 整个列表生成需求和用例xml
        xml_name = xmind_msg + ".xml"
        xml_req_name =  xmind_msg + "_req.xml"
        xml_path = os.path.join(output_dir, xml_name)
        xml_req_path = os.path.join(output_dir, xml_req_name)
        out = ET.Element(dx.case_tag['ts'], attrib = {"name" : xmind_msg})
        req_out = ET.Element(dx.req_tag['root'])
        if name != '':
            req_total = ET.SubElement(req_out, dx.req_tag['rqs'], attrib = \
                {"title" : name, "doc_id" : root_id})
        else:
            req_total = req_out
        reqs_id = root_id
        id_count = 1
        if auto_id:
            for xmind_file in xmind_file_list:
                try :
                    root_dict, req_dict = xd.start(xmind_file)
                    if need_case:
                        #print(root_dict)
                        dx.get_case_xml(root_dict['suites'][0], out, api = is_api)
                    if need_req:
                        #print(req_dict)
                        if req_dict['suites'] != []:
                            dx.get_req_xml(req_dict['suites'][0], req_total, auto_id, root_id)
                        if req_dict['cases'] != []:
                            dx.get_case_req_xml(req_dict['cases'], req_total, auto_id, root_id)
                    print("SUCCESS \t" + xmind_file)
                except Exception as e:
                    print(e)
                    print('\033[1;31mFAILED \t%s\033[m'%xmind_file)
            if need_case:
                save_xml(dx, out, xml_path)
            if need_req:
                save_xml(dx, req_out, xml_req_path)
        else:
            for xmind_file in xmind_file_list:
                try :
                    root_id = reqs_id + "." + str(id_count)
                    id_count += 1
                    root_dict, req_dict = xd.start(xmind_file)
                    if req_dict['suites'] != []:
                        dx.get_req_xml(req_dict['suites'][0], req_total, auto_id, root_id)
                    if req_dict['cases'] != []:
                        dx.get_case_req_xml(req_dict['cases'], req_total, auto_id, root_id)
                    print("req_SUCCESS \t" + xmind_file)
                except Exception as e:
                    print(e)
                    print('\033[1;31mreq_FAILED \t%s\033[m'%xmind_file)
            #先保存出需求的xml
            save_xml(dx,  req_out, xml_req_path)
            #读取需求xml中的id信息
            dx.read_req_id_dict(xml_req_path)
            #生成用例xml时，填入读取的id
            if need_case:
                for xmind_file in xmind_file_list:
                    try:
                        root_dict, req_dict = xd.start(xmind_file)
                        dx.get_case_xml(root_dict['suites'][0], out, api = is_api, \
                                argv = '', auto_id = False, name = name)
                        print("case_SUCCESS \t" + xmind_file)
                    except Exception as e:
                        print(e)
                        print('\033[1;31mcase_FAILED \t%s\033[m'%xmind_file)
                #最后保存用例xml
                save_xml(dx, out, xml_path)

def main():
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    parser = argparse.ArgumentParser(description = "")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dir', dest='dir', metavar='Dir', nargs="+",
            help='xmind file directory')
    group.add_argument('-f', '--file', dest='file', metavar='File', nargs="+",
            help='xmind file')
    parser.add_argument('-t', '--type', dest='file_type', choices=['req','case'], default='case',
            required=True,
            help='xmind file type')
    parser.add_argument('-i', '--id', dest='root_id', metavar='ID', nargs=1,
            help='req root docid')
    parser.add_argument('-n', '--name', dest='total_name', metavar='Name', nargs=1,
            help='describe the total xmind')
    parser.add_argument('-a', '--api', dest='is_api_case', action='store_const', const=True,
            default=False,
            help='xmind case file is api case')
    parser.add_argument('-r', '--req', dest='req_xml', action='store_const', const=True,
            default=False,
            help='create req xml')
    parser.add_argument('-c', '--case', dest='case_xml', action='store_const', const=True,
            default=False,
            help='create case xml')
    parser.add_argument('-s', '--single', dest='single', action='store_const', const=True,
            default=False,
            help='one xmind to one xml')
    args = parser.parse_args()
    print(args)

    xmind_type = args.file_type
    test_dir_list = args.dir
    test_file_list = args.file
    is_api = args.is_api_case
    need_req = args.req_xml
    need_case = args.case_xml
    single_create = args.single

    xd = xmind_to_dict.XmindToDict(xmind_type)
    dx = dict_to_xml.DictToXml()
    if args.total_name != None:
        name = args.total_name[0]
    else:
        name = ''

    if args.root_id != None:
        auto_id = 0
        root_id = args.root_id[0]
    else:
        auto_id = 1
        root_id = "demo1"

    if args.dir != None:
        for xmind_dir in test_dir_list:
            xmind_file_list = get_flist(xmind_dir)
            xmind_msg = os.path.basename(xmind_dir.strip("/"))
            run(xmind_file_list, xmind_type, is_api, xmind_msg, xd, dx, output_dir, \
                    need_req, need_case, single_create, auto_id, root_id, name)
    if args.file != None:
            xmind_msg = "file"
            run(test_file_list, xmind_type, is_api, xmind_msg, xd, dx, output_dir, \
                    need_req, need_case, single_create, auto_id, root_id, name)
        

if __name__ == "__main__":
    main()
