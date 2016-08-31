from jinja2 import Environment, FileSystemLoader
import xml.etree.ElementTree as et
import os
import sys
from code_generator import code_generator
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(THIS_DIR, os.pardir))


def bind_variables(xml_info: dict, template_variables: dict):
	code_generator.bind_common_variables(xml_info, template_variables)

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

	output_file = open(PARENT_DIR+"/Samples/output.py", "w")
	output_file.write(template.render(template_variables))
	output_file.close()

	print("Code is generated")
