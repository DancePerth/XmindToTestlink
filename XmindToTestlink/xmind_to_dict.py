# -*- coding: utf-8 -*-

import json
from zipfile import  ZipFile

class XmindToDict(object):
    def __init__(self, xmind_type = "case"):
        '''
        type = "case" 按用例设计规则解析xmind文件
        type = "req" 按需求分析规则解析xmind文件
        '''
        self.type = xmind_type

    def open_xmind(self, file_path):
        '''
        打开xmind文件，返回其中的内容
        '''
        target_file = "content.json"
        with ZipFile(file_path) as xmind:
            for f in xmind.namelist():
                if f == target_file:
                    return (xmind.open(f).read().decode('utf-8'))

    def create_suite(self, name, suite_detail = ''):
        suite = {
                'title':'',
                'detail':'',
                'suites':[],
                'cases':[]
                }
        suite['title'] = name.strip(" .,").replace(' ','')
        suite['detail'] = suite_detail
        return suite
    
    def get_summery(self, in_dict):
        return in_dict['plain']['content']
    
    def get_custom_fields(self, in_data):
        customs = []
        for attach in in_data['children']['attached']:
            if isinstance(attach, dict):
                custom = {}
                if "children" in attach and attach['children'] != {}:
                    custom[attach['title']] = attach['children']['attached'][0]['title']
                else:
                    custom[attach['title']] = ""
                customs.append(custom)
        return customs
    
    def get_steps(self, in_data):
        steps = []
        for attach in in_data['children']['attached']:
            if isinstance(attach, dict):
                step = {}
                if "children" in attach and attach['children'] != {}:
                    step[attach['title']] = attach['children']['attached'][0]['title']
                else:
                    step[attach['title']] = ""
                steps.append(step)
        return steps
    
    def get_execution_type(self, in_data):
        if in_data == "自动":
            return 2
        elif in_data == "手动":
            return 1
        else:
            return 2
    
    def create_case(self, in_data, pre_dict, num, req_spec, req):
        case = {
                'title':'',
                'summary':'',
                'preconditions':'',
                'importance':'',
                'execution_type':2,
                'custom_field':'',
                'step':'',
                'reqband':''
                }
        if req != '' and req_spec != '':
            case['reqband'] = {req: req_spec}
        if req_spec != '' and req == '':
            case['reqband'] = {req_spec: ''}
        if "title" in in_data.keys():
            case['title'] = in_data['title'].strip(" .,").replace('','')
        if "notes" in in_data.keys():
            case['summary'] = self.get_summery(in_data['notes'])
        if "children" in in_data.keys() and in_data['children'] != {}:
            if "attached" in in_data['children']:
                for attach in in_data['children']['attached']:
                    if isinstance(attach, dict):
                        if attach['title'] == "属性" and "children" in attach and attach['children'] != {}:
                            case['custom_field'] = self.get_custom_fields(attach)
                            if "执行方式" in case['custom_field']:
                                case['execution_type'] = self.get_execution_type(case['custom_field']['执行方式'])
                                del case['custom_field']['执行方式']
                        elif attach['title'] == "步骤" and "children" in attach and attach['children'] != {}:
                            case['step'] = self.get_steps(attach)
        if "markers" in in_data.keys():
            for mark in in_data['markers']:
                for k,v in mark.items():
                    if v == "task-done":
                        msg = {}
                        msg['code'] = 'yes'
                        if case['custom_field'] == '':
                            case['custom_field'] = []
                            case['custom_field'].append(msg)
                        else:
                            case['custom_field'].append(msg)
                    if v.find("priority-") >= 0:
                        pri = v.split('-')[1]
                        if pri == '1':
                            case['importance'] = 3
                        elif pri == '2':
                            case['importance'] = 2
                        elif pri == '3':
                            case['importance'] = 1
        if pre_dict != {}:
            for k,v in pre_dict.items():
                if k == str(num):
                    case['preconditions'] = v
        return case

    def have_case(self, in_data):
        msg = "\'title\': \'用例\'"
        if str(in_data).find(msg) >= 0:
            return 1
        else:
            return 0
    
    def is_case(self, in_data):
        for branch in in_data['children']['attached']:
            if branch['title'] == "属性" or branch['title'] == "步骤":
                return 1
    
    def check_suite_or_case(self, in_data):
        if "children" not in in_data.keys() or in_data['children'] == {}\
                or self.is_case(in_data):
                    return "case"
        else:
            return  "suite"

    def is_req(self, in_data):
        for branch in in_data['children']['attached']:
            if branch['title'] == "用例":
                return 1

    def check_reqs_or_req(self, in_data):
        if "children" not in in_data.keys() or in_data['children'] == {}\
                or self.is_req(in_data):
                    return "req"
        else:
            return  "reqs"
    
    def get_req_dict(self, in_data, out_dict, start = 0):
        if not self.have_case(in_data) and start == 0:
            return 0
        else:
            if "title" in in_data.keys():
                if in_data['title'] == "用例":
                    start = 1
                    return 0
                elif in_data['title'] != "用例":
                    sc = self.check_reqs_or_req(in_data)
                    if sc == "req":
                        case = self.create_case(in_data, pre_dict = {}, num = 0, req_spec = '', req = '')
                        out_dict['cases'].append(case)
                        return 1
                    elif sc == "reqs":
                        suite_detail = ""
                        if "notes" in in_data.keys():
                            suite_detail = in_data["notes"]["plain"]["content"]
                        suite = self.create_suite(in_data['title'], suite_detail)
                        out_dict['suites'].append(suite)
                        out_dict = suite
            if "notes" in in_data.keys():
                #需求的范围
                suite_detail = in_data["notes"]["plain"]["content"]
            if "children" in in_data.keys():
                if "attached" in in_data['children']:
                    #递归，遍历嵌套的节点
                    for count in range(len(in_data['children']['attached'])):
                        attach = in_data['children']['attached'][count]
                        if isinstance(attach, dict):
                            self.get_req_dict(attach, out_dict, start)

    def get_dict(self, in_data, out_dict, start = 0, pre_dict = {}, count = 0, req_spec = '', req = ''):
        def parse_xmind(in_data, out_dict, start = 0, pre_dict = {}, count = 0, req_spec = '', req = ''):
            if "title" in in_data.keys():
                if in_data['title'] == "用例":
                    start = 1
                elif in_data['title'] != "用例":
                    sc = self.check_suite_or_case(in_data)
                    if sc == "case":
                        case = self.create_case(in_data, pre_dict, count, req_spec, req)
                        out_dict['cases'].append(case)
                        return 1
                    elif sc == "suite":
                        #req_spec 和 req 给需求绑定用
                        if start == 0:
                            if req_spec == '':
                                req_spec = in_data['title']
                            elif req == '':
                                req = req_spec + "/" + in_data['title']
                            else:
                                req_spec = req.split('/')[-1]
                                req = req + "/" + in_data['title']
                        #count 和pre_dict 给用例前提用
                        count = 0
                        pre_dict = {}
                        suite_detail = ""
                        if "notes" in in_data.keys():
                            suite_detail = in_data["notes"]["plain"]["content"]
                        suite = self.create_suite(in_data['title'], suite_detail)
                        out_dict['suites'].append(suite)
                        out_dict = suite
            if "notes" in in_data.keys():
                #测试集的摘要
                suite_detail = in_data["notes"]["plain"]["content"]
            if "summaries" in in_data.keys():
                #测试用例的前提的位置
                for pre in in_data["summaries"]:
                    pre_dict[pre['range'].split(',')[0].split("(")[1]] = pre['topicId']
            if "children" in in_data.keys():
                if "summary" in in_data["children"]:
                    #测试用例的前提
                    for pre in in_data["children"]['summary']:
                        for k,v in pre_dict.items():
                            if pre['id'] == v:
                                pre_dict[k] = pre['title']
                if "attached" in in_data['children']:
                    #递归，遍历嵌套的节点
                    for count in range(len(in_data['children']['attached'])):
                        attach = in_data['children']['attached'][count]
                        if isinstance(attach, dict):
                            self.get_dict(attach, out_dict, start, pre_dict, count, req_spec, req)

        if self.type == "case":
            if not self.have_case(in_data) and start == 0:
                return 0
            else:
                parse_xmind(in_data, out_dict, start, pre_dict, count, req_spec, req)
        elif self.type == "req":
            parse_xmind(in_data, out_dict, start, pre_dict, count)
    
    def get_root(self, in_dict):
        root_name = in_dict[0]['title']
        return root_name

    def start(self, xmind_file):
        js_str = str(self.open_xmind(xmind_file))
        js_dict = json.loads(js_str)
        root_name = self.get_root(js_dict)
        root_dict = self.create_suite(root_name)
        if self.type == "case":
            self.get_dict(js_dict[0]['rootTopic'], root_dict)
            req_name = self.get_root(js_dict)
            req_dict = self.create_suite(root_name)
            self.get_req_dict(js_dict[0]['rootTopic'], req_dict)
            return root_dict, req_dict
        elif self.type == "req":
            req_name = self.get_root(js_dict)
            req_dict = self.create_suite(root_name)
            self.get_dict(js_dict[0]['rootTopic'], req_dict)
            return root_dict, req_dict

if __name__ == "__main__":
    js_file = "content.json"
    with open(js_file) as jf:
        js_dict = json.load(jf)
    xd = XmindToDict()
    root_dict = {}
    root_name = xd.get_root(js_dict)
    root = xd.create_suite(root_name)
    xd.get_req_dict(js_dict[0]['rootTopic'],root)
    print(root['suites'][0])
