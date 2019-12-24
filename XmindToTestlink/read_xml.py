import xml.etree.ElementTree as ET

tag = {
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

def get_suite(name, suite_detail = ''):
    suite = {
            'title':'',
            'detail':'',
            'suites':[],
            'cases':[]
            }
    suite['title'] = name
    suite['detail'] = suite_detail
    return suite

def get_cdata(elem, path):
    #cdata = elem.findtext(path).strip("<p></p>\t\n")
    #cdata = elem.findtext(path).replace('\t','').replace('\n','').strip("<p></p>")
    cdata = elem.findtext(path)
    return cdata

def get_case(elem):
    case = {
            'title':'',
            'summary':'',
            'preconditions':'',
            'importance':'2',
            'execution_type':'',
            'custom_field':'',
            'step':''
            }

    if elem.attrib != {}:
        case['title'] = elem.attrib['name']
    if elem.find(tag['sm']) != None:
        case['summary'] = get_cdata(elem, tag['sm'])
    if elem.find(tag['pc']) != None:
        case['preconditions'] = get_cdata(elem, tag['pc'])
    if elem.find(tag['et']) != None:
        case['execution_type'] = get_cdata(elem, tag['et'])
    if elem.find(tag['ip']) != None:
        case['importance'] = get_cdata(elem, tag['ip'])
    if elem.find(tag['sts']) != None:
        case['step'] = []
        for step in elem.findall(tag['sts'] + "/" + tag['st']):
            case['step'].append({get_cdata(step, tag['ac']): get_cdata(step, tag['ep'])})
    if elem.find(tag['cfs']) != None:
        case['custom_field'] = []
        for custom in elem.findall(tag['cfs'] + "/" + tag['cf']):
            if custom.findtext(tag['val']) != '' :
                case['custom_field'].append({custom.findtext(tag['nm']): custom.findtext(tag['val'])})
        if case['custom_field'] == []:
            case['custom_field'] = ''
    return case

def get_case_dict(elem, out_dict):
    if elem.tag == "testsuite":
        suite_name = elem.attrib['name']
        if elem.find(tag['dt']) != None:
            suite_detail = get_cdata(elem, tag['dt'])
        else :
            suite_detail = ''
        suite = get_suite(suite_name, suite_detail)
        out_dict['suites'].append(suite)
        out_dict = suite
        for child in elem:
            if child.tag == 'details':
                pass
            elif child.tag == 'testcase':
                out_dict['cases'].append(get_case(child))
            elif child.tag == 'testsuite':
                get_case_dict(child, out_dict)

def read_req_id(elem):
    if elem.find("docid") != None:
        req_id = get_cdata(elem, 'docid')
    if elem.find("title") != None:
        tmp_name = get_cdata(elem, 'title')
    return req_id, tmp_name



def get_req_id_dict(elem, pre_name = ''):
    id_dict = {}
    tmp_name = elem.attrib['title']
    req_id = elem.attrib['doc_id']
    req_name = pre_name + "/" + tmp_name
    pre_name = req_name
    id_dict[req_name] = req_id
    for child in elem:
        if child.tag == 'requirement':
            req_id, tmp_name = read_req_id(child)
            req_name = pre_name + "/" + tmp_name
            id_dict[req_name] = req_id
        elif child.tag == 'req_spec':
            id_dict.update(get_req_id_dict(child, pre_name))
    return id_dict

def read_case_xml(xml_file):
    tree = ET.ElementTree(file = xml_file)
    root = tree.getroot()
    out_dict = get_suite("最外层")
    get_case_dict(root, out_dict)
    return aaa['suites'][0]

def cdata(element, content):
    '''
    添加xml中的cdata标签
    '''
    if isinstance(content, int):
        content = str(content)
    content = content.replace("\n", "<br />")  # replace new line for *nix system
    element.append(ET.Comment(' --><![CDATA[' + content + ']]><!-- '))

def read_req_id_xml(xml_file):
    tree = ET.ElementTree(file = xml_file)
    root = tree.getroot()
    id_dict = {}
    req_out = ET.Element('requirements')
    for child in root:
        if child.tag == 'req_spec':
            if id_dict == {}:
                id_dict = get_req_id_dict(child)
            else:
                id_dict.update(get_req_id_dict(child))
        if child.tag == 'requirement':
            req_id, tmp_name = read_req_id(child)
            req_name = "/" + tmp_name
            id_dict[req_name] = req_id
            tc = ET.SubElement(req_out, 'requirement')
            tt = ET.SubElement(tc, 'title')
            cdata(tt, tmp_name)
            rid = ET.SubElement(tc, 'docid')
            cdata(rid, req_id)
    #id_dict['root_req_spec'] = child.attrib['title']
    if req_out.__len__() > 0:
        xml_path = xml_file.replace('req.xml','requirement.xml')
        w = ET.ElementTree(req_out)
        w.write(xml_path, 'utf-8', True)
    return id_dict

if __name__ == "__main__":
    #print(read_case_xml('./demo.xml'))
    print(read_req_id_xml('./case_req.xml'))
    #read_req_id_xml('./backup.xml')
