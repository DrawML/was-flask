import xml.etree.ElementTree as et
from flask import current_app
from app.experiment.object_code.scripts.code_generator import TemplateError, \
    get_template, parse_xml, process_data, make_optimizer, bind_common_variables


def bind_variables(xml_info: dict, template_variables: dict):
    bind_common_variables(xml_info, template_variables)

    x_shape = xml_info['input_x']
    x_shape.replace(' ', '')
    x_ver = int(x_shape.split(',')[0])
    x_hor = int(x_shape.split(',')[1])
    template_variables['x_vertical'] = x_ver
    template_variables['x_horizontal'] = x_hor
    template_variables['y_size'] = int(xml_info['input_y'])

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


def make_code(root: et.Element):
    try:
        template = get_template(root.find("model").find("type").text)
    except TemplateError as e:
        current_app.logger.err(e)
        return
    xml_info = dict()
    parse_xml("", root, root, xml_info)

    template_variables = dict()

    bind_variables(xml_info, template_variables)
    process_data(xml_info, template_variables)
    make_optimizer(xml_info, template_variables)

    return template.render(template_variables)
