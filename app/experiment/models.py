import json
import os
import xml.etree.ElementTree as Et
from app.db_models import Experiment


class ExperimentError(Exception):
	pass


class TFConverter:
	"""This code is NOT considered about exception"""
	SCRIPT_MODULE = 'app.experiment.object_code.scripts'
	def __init__(self, xml):
		if os.path.isfile(xml) is True:
			xml_tree = Et.parse(xml)
			xml_tree.getroot()
		else:
			xml_tree = Et.fromstring(xml)

		self.root = xml_tree
		if self.root.tag != "experiment":
			raise ExperimentError()

	def process_data(self):
		"""data process module will be here"""
		pass

	def generate_object_code(self):
		# have to consider about exception
		model_type = self.root.find("model").find("type").text
		script_module = __import__(self.SCRIPT_MODULE, globals(),
		                           locals(), [model_type], 0)
		object_script = getattr(script_module, model_type)
		object_script.make_code(self.root)


class Refiner(json.JSONEncoder):
	def __init__(self, exps):
		self.exps = []
		for exp in exps:
			temp = self.exp_to_dict(exp)
			self.exps.append(temp)

	def exp_to_dict(self, exp):
		exp_dict = dict(
			id=exp.id,
			date_modified=str(exp.date_modified),
			date_created=str(exp.date_created),
			user_id=exp.user_id,
			name=exp.name,
			xml=exp.xml.decode(),
			drawing=exp.drawing.decode(),
			input=exp.input
		)
		return exp_dict


class JsonParser:
	@staticmethod
	def parse_post(json):
		try:
			exp_json = json['exp_data']
			exp_data = Experiment(exp_json['name'],
			                      exp_json['user_id'],
			                      exp_json['xml'].encode(),
			                      exp_json['drawing'].encode(),
			                      exp_json['input'])
		except KeyError as e:
			return e
		return exp_data
