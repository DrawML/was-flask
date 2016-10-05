import xml.etree.ElementTree as et
from jinja2.exceptions import TemplateError
from app.common.object_code.scripts.code_generator import get_template, \
    parse_xml, process_data, make_optimizer, bind_common_variables, get_input_shape


def bind_variables(xml_info: dict, template_variables: dict):
    bind_common_variables(xml_info, template_variables)

    shapes = get_input_shape(xml_info, template_variables)

    x_shape = shapes[0]
    y_shape = shapes[1]
    template_variables['x_vertical'] = x_shape[0]
    template_variables['x_horizontal'] = x_shape[1]
    template_variables['y_size'] = y_shape[0]

    template_variables['layer_size'] = int(xml_info['layer_set_layer_size'])
    template_variables['rnn_size'] = int(xml_info['layer_set_rnn_size'])
    template_variables['time_step_size'] = int(xml_info['layer_set_time_step_size'])
    template_variables['batch_size'] = int(xml_info['layer_set_batch_size'])

    cell_type = xml_info['1_layer_type']
    if cell_type == 'rnn':
        template_variables['cell_type'] = "'rnn'"
    elif cell_type == 'lstm':
        template_variables['cell_type'] = "'lstm'"
    elif cell_type == 'gru':
        template_variables['cell_type'] = "'gru'"


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

    return template.render(template_variables), data
