import xml.etree.ElementTree as et
from jinja2.exceptions import TemplateError
from app.experiment.object_code.scripts.code_generator \
    import get_template, parse_xml


def bind_variables(xml_info, template_variable):
    ids = xml_info['input_data']
    ids.replace(' ', '')
    template_variable['file_ids'] = ids.split(',')


def find_key(num: int, xml: dict):
    if str(num) + '_concat_data' in xml:
        return str(num) + '_concat_data', 'concat'
    elif str(num) + '_transpose_data' in xml:
        return str(num) + '_transpose_data', 'transpose'


def make_processing(xml_info, template_variable):
    size = int(xml_info['data_processing_size'])
    template_variable['processing_size'] = size

    columns = xml_info['input_col']
    columns = columns.replace(' ', '')
    columns = columns.split(',')
    columns = [int(i) for i in columns]
    total_col = 0
    for col in columns:
        total_col += col
    template_variable['columns'] = columns


    processing = []

    for i in range(size):
        unit = {}
        key, p_type = find_key(i+1, xml_info)

        unit['type'] = p_type

        data_str = xml_info[key]
        data_str = data_str.replace(' ', '')
        unit['data'] = data_str.split(',')

        unit['shape'] = [-1, total_col]
        unit['name'] = 'seq' + str(i+1)
        processing.append(unit)

    template_variable['processing'] = processing


def make_code(root: et.Element):
    try:
        template = get_template("data_processing")
    except TemplateError as e:
        raise e
    xml_info = dict()
    parse_xml("", root.find("data_processing"), root.find("data_processing"), xml_info)
    parse_xml("", root.find("input"), root.find("input"), xml_info)

    require = None
    if root.find('model') is not None:
        if root.find('model').find('data') is not None:
            require = root.find("model").find("data").text
        else:
            raise Exception("Invalid XML")

    template_variables = dict()
    template_variables['require'] = require
    bind_variables(xml_info, template_variables)
    make_processing(xml_info, template_variables)

    return template.render(template_variables)
