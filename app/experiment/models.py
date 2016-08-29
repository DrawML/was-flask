import json
from app.db_models import Experiment

class exp_refiner(json.JSONEncoder):
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


class exp_json_parser():
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

