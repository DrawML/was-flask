from jinja2 import Environment, FileSystemLoader
import xml.etree.ElementTree as et
import os
import sys
from code_generator import code_generator
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(THIS_DIR, os.pardir))


def bind_variables(xml_info: dict, template_variables: dict):
	code_generator.bind_common_variables(xml_info, template_variables)

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

			activ_func = code_generator.make_activation_function(xml_info[num + '_activation_type'])
			layer['activ_func'] = activ_func
			layer['activ_strides_v'] = int(xml_info[num + '_activation_strides_vertical'])
			layer['activ_strides_h'] = int(xml_info[num + '_activation_strides_horizontal'])
			layer['activ_padding'] = code_generator.bind_padding(xml_info[num + '_activation_padding'])

			pooling = code_generator.make_pooling(xml_info[num + '_pooling_type'])
			layer['pooling'] = pooling
			layer['pooling_strides_v'] = int(xml_info[num + '_pooling_strides_vertical'])
			layer['pooling_strides_h'] = int(xml_info[num + '_pooling_strides_horizontal'])
			layer['pooling_padding'] = code_generator.bind_padding(xml_info[num + '_pooling_padding'])

			layer['input_x'] = int(xml_info[num + '_layer_input_x'])
			layer['input_y'] = int(xml_info[num + '_layer_input_y'])
			layer['input_z'] = int(xml_info[num + '_layer_input_z'])
			layer['output'] = int(xml_info[num + '_layer_output'])

		elif xml_info[num + '_layer_type'] == 'none' or xml_info[num + '_layer_type'] == 'out':
			layer['type'] = xml_info[num + '_layer_type']

			activ_func = code_generator.make_activation_function(xml_info[num + '_layer_activation'])
			layer['activ_func'] = activ_func
			layer['input'] = int(xml_info[num + '_layer_input'])
			layer['output'] = int(xml_info[num + '_layer_output'])

		layers.append(layer)

	template_variables['layers'] = layers


def make_code(root: et.Element):
	j2_env = Environment(loader=FileSystemLoader(PARENT_DIR),
	                     trim_blocks=True)
	try:
		template = j2_env.get_template("./Template Files/template_" + root.find("model").find("type").text + ".py")
	except:
		print("template error")
		sys.exit(2)

	xml_info = dict()
	code_generator.parse_xml("", root, root, xml_info)

	template_variables = dict()

	bind_variables(xml_info, template_variables)
	code_generator.process_data(xml_info, template_variables)
	code_generator.make_optimizer(xml_info, template_variables)
	code_generator.make_initializer(xml_info, template_variables)

	output_file = open(PARENT_DIR+"/Samples/output.py", "w")
	output_file.write(template.render(template_variables))
	output_file.close()

	print("Code is generated")
