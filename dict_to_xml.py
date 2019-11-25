# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET

class DictToXml(object):
    def __init__(self):
        self.case_tag = {
                "ts":"testsuite",
                "tc":"testcase",
                "dt":"details",
                "sm":"summary",
                "cfs":"custom_fields",
                "cf":"custom_field",
                "sts":"steps",
                "st":"step",
                "sn":"step_number",
                "ac":"actions",
                "ep":"expectedresults",
                "pc":"preconditions",
                "ip":"importance",
                "et":"execution_type",
                "nm":"name",
                "val":"value"
            }
        self.req_tag = {
                "root":"requirement-specification",
                "rqs":"req_spec",
                "rq":"requirement",
                "id":"docid",
                "title":"title",
                "cfs":"custom_fields",
                "cf":"custom_field",
                "nm":"name",
                "val":"value",
                "dt":"scope",
                "sm":"description"
                }

    def cdata(self, element, content):
        '''
        添加xml中的cdata标签
        '''
        if isinstance(content, int):
            element.text = str(content)
        elif content:
            content = content.replace("\n", "<br />")  # replace new line for *nix system
            #element.append(ET.Comment(' --><![CDATA[<p>' + content + '</p>]]><!-- '))
            element.append(ET.Comment(' --><![CDATA[' + content + ']]><!-- '))
    
    
    def indent(self, elem, level=0):
        '''
        添加xml文件的换行符,增强可读性
        '''
        i = "\n" + level*"\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def get_req_xml(self, in_dict, node = '', root_id = "demo1", id_count = 1):
        '''
        解析输入字典，按照需求格式,生成xml
        '''
        if "title" in in_dict.keys():
            #添加需求规约
            if node == '':
                root = ET.Element(self.req_tag['root'])
                ts = ET.SubElement(root, self.req_tag['rqs'], attrib = {"title" : in_dict['title'], "doc_id" : root_id})
                reqs_id = root_id
            else:
                reqs_id = root_id
                ts = ET.SubElement(node, self.req_tag['rqs'], attrib = {"title" : in_dict['title'], "doc_id" :reqs_id})
            if "detail" in in_dict.keys() and in_dict['detail'] != '':
                dt = ET.SubElement(ts, self.req_tag['dt'])
                self.cdata(dt, in_dict['detail'])
        if "cases" in in_dict.keys() and in_dict['cases'] != []:
            #添加需求
            for case in in_dict['cases']:
                req_id = reqs_id + "." +  str(id_count)
                id_count += 1
                tc = ET.SubElement(ts, self.req_tag['rq'])            
                tt = ET.SubElement(tc, self.req_tag['title'])
                self.cdata(tt, case['title'])
                rid = ET.SubElement(tc, self.req_tag['id'])
                self.cdata(rid, req_id)
                if case[self.case_tag['sm']] != '':
                    sm = ET.SubElement(tc, self.req_tag['sm'])
                    self.cdata(sm, case[self.case_tag['sm']])
                if case[self.req_tag['cf']] != '':
                    cfs = ET.SubElement(tc, self.req_tag['cfs'])
                    for custom_field in  case[self.req_tag['cf']]:
                        cf = ET.SubElement(cfs, self.req_tag['cf'])
                        for k,v in custom_field.items():
                            nm = ET.SubElement(cf, self.req_tag['nm'])
                            self.cdata(nm, k)
                            val = ET.SubElement(cf, self.req_tag['val'])
                            self.cdata(val, v)
        if "suites" in in_dict.keys() and in_dict['suites'] != []:
            #递归，遍历嵌套的需求规约
            for suite in in_dict['suites']:
                root_id = reqs_id + "." + str(id_count)
                id_count += 1
                self.get_req_xml(suite, ts, root_id)
        if node == '':
            #返回xml根节点
            return root
    
    def get_case_xml(self, in_dict, node = '', api = False, argv = ''):
        '''
        解析输入字典，按照用例格式，生成xml
        '''
        if "title" in in_dict.keys():
            #添加测试集
            if api == True:
                argv += "<li>" + in_dict['title'] + "</li>"
            #if node == '':
            #    ts = ET.Element(self.case_tag['ts'], attrib = {"name" : in_dict['title']})
            #else:
            ts = ET.SubElement(node, self.case_tag['ts'], attrib = {"name" : in_dict['title']})
            if "detail" in in_dict.keys() and in_dict['detail'] != '':
                dt = ET.SubElement(ts, self.case_tag['dt'])
                self.cdata(dt, in_dict['detail'])
        if "cases" in in_dict.keys() and in_dict['cases'] != []:
            for case in in_dict['cases']:
                #添加测试用例
                tc = ET.SubElement(ts, self.case_tag['tc'], attrib = {"name":case['title']})            
                if case[self.case_tag['pc']] != '':
                    #添加前提
                    pc = ET.SubElement(tc, self.case_tag['pc'])
                    self.cdata(pc, case[self.case_tag['pc']])
                if case[self.case_tag['sm']] != '' or api == True:
                    #添加摘要
                    sm = ET.SubElement(tc, self.case_tag['sm'])
                    msg = case[self.case_tag['sm']]
                    if api == True:
                        case_argv = argv + "<li>" + case['title'] + "</li>"
                        msg = msg + "\n\n参数设置: \n" + "<ul>" + case_argv + "</ul>"
                    self.cdata(sm, msg)
                if case[self.case_tag['ip']] != '':
                    #添加优先级
                    ip = ET.SubElement(tc, self.case_tag['ip'])
                    self.cdata(ip, case[self.case_tag['ip']])
                if case[self.case_tag['et']] != '':
                    #添加执行方式
                    et = ET.SubElement(tc, self.case_tag['et'])
                    self.cdata(et, case[self.case_tag['et']])
                if case[self.case_tag['st']] != '':
                    #添加步骤
                    sts = ET.SubElement(tc, self.case_tag['sts'])
                    for n in range(len(case[self.case_tag['st']])):
                        step = case[self.case_tag['st']][n]
                        st = ET.SubElement(sts, self.case_tag['st'])
                        for k,v in step.items():
                            sn = ET.SubElement(st, self.case_tag['sn'])
                            self.cdata(sn,n+1)
                            ac = ET.SubElement(st, self.case_tag['ac'])
                            self.cdata(ac,k)
                            ep = ET.SubElement(st, self.case_tag['ep'])
                            self.cdata(ep,v)
                if case[self.case_tag['cf']] != '':
                    #添加自定义字段
                    cfs = ET.SubElement(tc, self.case_tag['cfs'])
                    for custom_field in  case[self.case_tag['cf']]:
                        cf = ET.SubElement(cfs, self.case_tag['cf'])
                        for k,v in custom_field.items():
                            nm = ET.SubElement(cf, self.case_tag['nm'])
                            self.cdata(nm, k)
                            val = ET.SubElement(cf, self.case_tag['val'])
                            self.cdata(val, v)
        if "suites" in in_dict.keys() and in_dict['suites'] != []:
            #递归，遍历嵌套的测试集
            for suite in in_dict['suites']:
                self.get_case_xml(suite, ts, api, argv)
        return ts
