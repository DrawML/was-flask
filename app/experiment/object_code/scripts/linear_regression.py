from jinja2 import Environment, FileSystemLoader
import xml.etree.ElementTree as et
import os
import sys
from code_generator import code_generator
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(THIS_DIR, os.pardir))


def bind_variables(xml_info: dict, template_variables: dict):
	code_generator.bind_common_variables(xml_info, template_variables)


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
	code_generator.process_data(xml_info, template_variables)
	bind_variables(xml_info, template_variables)
	code_generator.make_optimizer(xml_info, template_variables)
	code_generator.make_initializer(xml_info, template_variables)

	output_file = open(PARENT_DIR+"/Samples/output.py", "w")
	output_file.write(template.render(template_variables))
	output_file.close()

	print("Code is generated")
