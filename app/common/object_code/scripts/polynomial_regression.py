import xml.etree.ElementTree as et
from jinja2.exceptions import TemplateError
from app.common.object_code.scripts.code_generator import get_template, \
    parse_xml, process_data, make_initializer, make_optimizer, bind_common_variables


def bind_variables(xml_info: dict, template_variables: dict):
    bind_common_variables(xml_info, template_variables)


def make_code(root: et.Element, template_name: str):
    try:
        template = get_template(template_name)
    except TemplateError as e:
        raise e

    xml_info = dict()
    parse_xml("", root, root, xml_info)

    template_variables = dict()
    data = process_data(xml_info, template_variables)
    bind_variables(xml_info, template_variables)
    make_optimizer(xml_info, template_variables)
    make_initializer(xml_info, template_variables)

    return template.render(template_variables), data
