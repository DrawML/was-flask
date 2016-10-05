import xml.etree.ElementTree as et
from jinja2.exceptions import TemplateError
from app.experiment.object_code.scripts.code_generator import get_template, \
    parse_xml, process_data, make_initializer, make_activation_function, \
    make_optimizer, bind_common_variables


def bind_variables(xml_info: dict, template_variables: dict):
    bind_common_variables(xml_info, template_variables)

    layer_size = int(xml_info['layer_set_size'])
    template_variables['layer_size'] = layer_size
    input_shape = []
    output_shape = []
    activ_functions = []
    for i in range(layer_size):
        activation_key = str(i + 1) + '_layer_activation'
        activ_functions.append(make_activation_function(xml_info[activation_key]))

        input_key = str(i + 1) + '_layer_input'
        output_key = str(i + 1) + '_layer_output'
        input_shape.append(int(xml_info[input_key]))
        output_shape.append(int(xml_info[output_key]))
    template_variables["activation_functions"] = activ_functions
    template_variables['input_shape'] = input_shape
    template_variables['output_shape'] = output_shape


def make_code(root: et.Element, template_name: str):
    try:
        template = get_template(template_name)
    except TemplateError as e:
        raise e
    xml_info = dict()
    parse_xml("", root, root, xml_info)

    template_variables = dict()

    bind_variables(xml_info, template_variables)
    data = process_data(xml_info, template_variables)
    make_optimizer(xml_info, template_variables)
    make_initializer(xml_info, template_variables)

    return template.render(template_variables), data
