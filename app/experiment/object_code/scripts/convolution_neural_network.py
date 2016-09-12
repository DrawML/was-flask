import xml.etree.ElementTree as et
from jinja2.exceptions import TemplateError
from app.experiment.object_code.scripts.code_generator import get_template, \
    parse_xml, process_data, make_initializer, make_activation_function, \
    make_optimizer, bind_common_variables, make_pooling, bind_padding


def bind_variables(xml_info: dict, template_variables: dict):
    bind_common_variables(xml_info, template_variables)

    template_variables['dropout_conv'] = xml_info['model_dropout_conv']
    template_variables['dropout_hidden'] = xml_info['model_dropout_hidden']

    x_shape = xml_info['input_x']
    x_shape.replace(' ', '')
    x_ver = int(x_shape.split(',')[0])
    x_hor = int(x_shape.split(',')[1])
    template_variables['x_vertical'] = x_ver
    template_variables['x_horizontal'] = x_hor
    template_variables['y_size'] = int(xml_info['input_y'])

    layer_size = int(xml_info['layer_set_size'])
    template_variables['layer_size'] = layer_size
    layers = []
    for i in range(layer_size):
        num = str(i + 1)

        layer = {}
        layer['num'] = int(num)

        if xml_info[num + '_layer_type'] == 'convolution':
            layer['type'] = 'conv'

            activ_func = make_activation_function(xml_info[num + '_activation_type'])
            layer['activ_func'] = activ_func
            layer['activ_strides_v'] = int(xml_info[num + '_activation_strides_vertical'])
            layer['activ_strides_h'] = int(xml_info[num + '_activation_strides_horizontal'])
            layer['activ_padding'] = bind_padding(xml_info[num + '_activation_padding'])

            pooling = make_pooling(xml_info[num + '_pooling_type'])
            layer['pooling'] = pooling
            layer['pooling_strides_v'] = int(xml_info[num + '_pooling_strides_vertical'])
            layer['pooling_strides_h'] = int(xml_info[num + '_pooling_strides_horizontal'])
            layer['pooling_padding'] = bind_padding(xml_info[num + '_pooling_padding'])

            layer['input_x'] = int(xml_info[num + '_layer_input_x'])
            layer['input_y'] = int(xml_info[num + '_layer_input_y'])
            layer['input_z'] = int(xml_info[num + '_layer_input_z'])
            layer['output'] = int(xml_info[num + '_layer_output'])

        elif xml_info[num + '_layer_type'] == 'none' or xml_info[num + '_layer_type'] == 'out':
            layer['type'] = xml_info[num + '_layer_type']

            activ_func = make_activation_function(xml_info[num + '_layer_activation'])
            layer['activ_func'] = activ_func
            layer['input'] = int(xml_info[num + '_layer_input'])
            layer['output'] = int(xml_info[num + '_layer_output'])

        layers.append(layer)

    template_variables['layers'] = layers


def make_code(root: et.Element):
    try:
        template = get_template(root.find("model").find("type").text)
    except TemplateError as e:
        raise e
    xml_info = dict()
    parse_xml("", root, root, xml_info)

    template_variables = dict()

    bind_variables(xml_info, template_variables)
    process_data(xml_info, template_variables)
    make_optimizer(xml_info, template_variables)
    make_initializer(xml_info, template_variables)

    return template.render(template_variables)

