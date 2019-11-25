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
        suite['title'] = name.strip(" .,")
        suite['detail'] = suite_detail
        return suite
    
    def get_summery(self, in_dict):
        return in_dict['plain']['content']
    
    def get_custom_fields(self, in_data):
        customs = []
        for attach in in_data['children']['attached']:
            if isinstance(attach, dict):
                custom = {}
                if "children" in attach:
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
                if "children" in attach:
                    step[attach['title']] = attach['children']['attached'][0]['title']
                else:
                    step[attach['title']] = ""
                steps.append(step)
        return steps
    
    def get_execution_type(self, in_data):
        if in_data['children']['attached'][0]['title'] == "自动":
            return 2
        elif in_data['children']['attached'][0]['title'] == "手动":
            return 1
    
    def create_case(self, in_data, pre_dict, num):
        case = {
                'title':'',
                'summary':'',
                'preconditions':'',
                'importance':'',
                'execution_type':'',
                'custom_field':'',
                'step':''
                }
        if "title" in in_data.keys():
            case['title'] = in_data['title'].strip(" .,")
        if "notes" in in_data.keys():
            case['summary'] = self.get_summery(in_data['notes'])
        if "children" in in_data.keys() and in_data['children'] != {}:
            if "attached" in in_data['children']:
                for attach in in_data['children']['attached']:
                    if isinstance(attach, dict):
                        if attach['title'] == "属性":
                            case['custom_field'] = self.get_custom_fields(attach)
                        elif attach['title'] == "步骤":
                            case['step'] = self.get_steps(attach)
                        elif attach['title'] == "执行方式":
                            case['execution_type'] = self.get_execution_type(attach)
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
                        case['importance'] = v.split('-')[1]
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
    
    
    def get_dict(self, in_data, out_dict, start = 0, pre_dict = {}, count = 0):
        def parse_xmind(in_data, out_dict, start = 0, pre_dict = {}, count = 0):
            if "title" in in_data.keys():
                if in_data['title'] == "用例":
                    start = 1
                elif in_data['title'] != "用例":
                    sc = self.check_suite_or_case(in_data)
                    if sc == "case":
                        case = self.create_case(in_data, pre_dict, count)
                        out_dict['cases'].append(case)
                        return 1
                    elif sc == "suite":
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
                            self.get_dict(attach, out_dict, start, pre_dict, count)

        if self.type == "case":
            if not self.have_case(in_data) and start == 0:
                return 0
            else:
                parse_xmind(in_data, out_dict, start, pre_dict, count)
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
        self.get_dict(js_dict[0]['rootTopic'], root_dict)
        return root_dict

if __name__ == "__main__":
    js_file = "content.json"
    with open(js_file) as jf:
        js_dict = json.load(jf)
    xd = XmindToDict()
    root_dict = {}
    root_name = xd.get_root(js_dict)
    root = xd.create_suite(root_name)
    xd.get_dict(js_dict[0]['rootTopic'],root)
    print(root['suites'][0])
