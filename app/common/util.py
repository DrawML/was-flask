import json
import os
import pickle
from enum import Enum
from xml.etree import ElementTree as Et

from app.experiment.object_code.scripts import data_process as data_process
from app.mysql_models import Experiment


class ExperimentError(Exception):
    pass


class TestError(Exception):
    pass


class GeneratorType(Enum):
    TRAIN = {"GENERATOR": "train", "TAG": "experiment"}
    TEST = {"GENERATOR": "test", "TAG": "test"}

    def __str__(self):
        return self.value["GENERATOR"]

    def get_tag_name(self):
        return self.value["TAG"]


class XMLTree:
    TYPE = GeneratorType

    def __init__(self, xml, xml_tree_type: GeneratorType):
        self.xml_tree_type = xml_tree_type

        if os.path.isfile(xml) is True:
            self.xml_tree = Et.parse(xml)
            self.xml_tree.getroot()
        else:
            self.xml_tree = Et.fromstring(xml)
        self.root = self.xml_tree
        if self.root.tag != self.xml_tree_type.get_tag_name():
            error = self.get_error()
            raise error()

    def get_error(self):
        if self.xml_tree_type == GeneratorType.TRAIN:
            return ExperimentError
        elif self.xml_tree_type == GeneratorType.TEST:
            return TestError


class DataProcessor:
    def __init__(self, xml):
        self.root = XMLTree(xml).root
        self.processing = self.root.find('data_processing')

    def generate_object_code(self):
        # have to consider about exception
        return data_process.make_code(self.root)

    def run_obj_code(self, obj_code):
        """This function just for test object code"""
        OUTPUT_PATH = '/Users/chan/test/output_data.py'
        output_file = open(OUTPUT_PATH, "w")
        output_file.write(obj_code)
        output_file.close()


class TFConverter:
    """This code is NOT considered about exception"""
    SCRIPT_MODULE = 'app.experiment.object_code.scripts'
    TYPE = GeneratorType

    def __init__(self, xml, converter_type: GeneratorType):
        self.root = XMLTree(xml, converter_type).root
        self.model_type = self.root.find("model").find("type").text
        self.converter_type = converter_type

    def generate_object_code(self):
        # have to consider about exception
        script_module = __import__(self.SCRIPT_MODULE, globals(),
                                   locals(), [self.model_type], 0)
        object_script = getattr(script_module, self.model_type)
        template_name = self.root.find("model").find("type").text + "_{0}".format(self.converter_type)
        return object_script.make_code(self.root, template_name)

    # have to be deprecated
    def run_obj_code(self, obj_code):
        """This function just for test object code"""
        OUTPUT_PATH = '/Users/chan/test/output{0}.py'.format(self.converter_type)
        output_file = open(OUTPUT_PATH, "w")
        output_file.write(obj_code)
        output_file.close()


class Refiner(json.JSONEncoder):
    def __init__(self, exps):
        super().__init__()
        if type(exps) is not list:
            self.exps = self.exp_to_dict(exps)
        else:
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
    def parse_post(json, user_id):
        try:
            exp_json = json['exp_data']
            exp_data = Experiment(exp_json['name'],
                                  user_id,
                                  pickle.dumps(exp_json['xml']),
                                  pickle.dumps(exp_json['drawing']),
                                  exp_json['input'])
        except KeyError as e:
            return e
        return exp_data
