import xml.etree.ElementTree as et
from code_generator import code_generator


def bind_variables(xml_info: dict, template_variables: dict):
	code_generator.bind_common_variables(xml_info, template_variables)

	layer_size = int(xml_info['layer_set_size'])
	template_variables['layer_size'] = layer_size
	input_shape = []
	output_shape = []
	activ_functions = []
	for i in range(layer_size):
		activation_key = str(i + 1) + '_layer_activation'
		activ_functions.append(code_generator.make_activation_function(xml_info[activation_key]))

		input_key = str(i + 1) + '_layer_input'
		output_key = str(i + 1) + '_layer_output'
		input_shape.append(int(xml_info[input_key]))
		output_shape.append(int(xml_info[output_key]))
	template_variables["activation_functions"] = activ_functions
	template_variables['input_shape'] = input_shape
	template_variables['output_shape'] = output_shape


def make_code(root: et.Element):
	template = code_generator.get_template(root.find("model").find("type").text)
	xml_info = dict()
	code_generator.parse_xml("", root, root, xml_info)

	template_variables = dict()

	bind_variables(xml_info, template_variables)
	code_generator.process_data(xml_info, template_variables)
	code_generator.make_optimizer(xml_info, template_variables)
	code_generator.make_initializer(xml_info, template_variables)

	output_file = open("/Users/chan/test/output.py", "w")
	output_file.write(template.render(template_variables))
	output_file.close()

	print("Code is generated")
