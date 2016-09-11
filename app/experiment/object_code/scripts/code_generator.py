import os
import xml.etree.ElementTree as et
from jinja2 import Environment, FileSystemLoader


class TemplateError(Exception):
    pass


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(THIS_DIR, os.pardir))


def get_template(model_type: str):
    j2_env = Environment(loader=FileSystemLoader(PARENT_DIR + '/templates'),
                         trim_blocks=True)
    template = None
    try:
        template = j2_env.get_template("/template_" + model_type)
    except:
        raise TemplateError
    finally:
        return template


def bind_common_variables(xml_info: dict, template_variables: dict):
    template_variables["training_epoch"] = xml_info["model_training_epoch"]

    if "regularization_enable" in xml_info:
        if xml_info["regularization_enable"] == "true":
            template_variables["reg_enable"] = True
            template_variables["reg_lambda"] = xml_info["regularization_lambda"]
        else:
            template_variables["reg_enable"] = False
            template_variables["reg_lambda"] = 0


def process_data(xml_info: dict, template_variables: dict):
    """
        data processing code...
    """

    # template_variables["x_data"] = xml_info["x_data"]
    # template_variables["y_data"] = xml_info["y_data"]


def make_initializer(xml_info: dict, template_variables: dict):
    initializer_type = xml_info["initializer_type"]

    if initializer_type == "random_uniform":
        params = dict()
        params["minval"] = float(xml_info["initializer_min"])
        params["maxval"] = float(xml_info["initializer_max"])

        template_variables["init_module"] = "tf.random_uniform"
        template_variables["init_params"] = params

    if initializer_type == "random_normal":
        params = dict()
        params["stddev"] = float(xml_info["initializer_stddev"])

        template_variables["init_module"] = "tf.random_normal"
        template_variables["init_params"] = params


def make_activation_function(activ_func_name: str):
    if activ_func_name == 'none':
        return 'no_module'
    if activ_func_name == "relu":
        return "tf.nn.relu"


def make_pooling(name: str):
    if name == 'none':
        return 'no_module'
    if name == "max":
        return "tf.nn.max_pool"


def bind_padding(name: str):
    if name == 'same':
        return "'SAME'"
    if name == "max":
        return "'VALID'"


def make_optimizer(xml_info: dict, template_variables: dict):
    opt_name = xml_info["optimizer_type"]
    learning_rate = float(xml_info["optimizer_learning_rate"])

    if opt_name == "gradient_descent":
        params = dict()
        params["learning_rate"] = learning_rate
        if "optimizer_use_locking" in xml_info:
            params["use_locking"] = xml_info["optimizer_use_locking"]
        if "optimizer_name" in xml_info:
            params["optimizer_name"] = xml_info["optimizer_name"]
        template_variables["optimizer_module"] = "tf.train"
        template_variables["optimizer_name"] = "'GradientDescentOptimizer'"
        template_variables["optimizer_params"] = params

    elif opt_name == "adadelta":
        params = dict()
        params["learning_rate"] = learning_rate
        if "optimizer_rho" in xml_info:
            params["rho"] = xml_info["optimizer_rho"]
        if "optimizer_epsilon" in xml_info:
            params["epsilon"] = xml_info["optimizer_epsilon"]
        if "optimizer_use_locking" in xml_info:
            params["use_locking"] = xml_info["optimizer_use_locking"]
        if "optimizer_name" in xml_info:
            params["name"] = xml_info["optimizer_name"]
        template_variables["optimizer_module"] = "tf.train"
        template_variables["optimizer_name"] = "'AdadeltaOptimizer'"
        template_variables["optimizer_params"] = params

    elif opt_name == "adagrad":
        params = dict()
        params["learning_rate"] = learning_rate
        if "optimizer_initial_accumulator_value" in xml_info:
            params["initial_accumulator_value"] = xml_info["optimizer_initial_accumulator_value"]
        if "optimizer_use_locking" in xml_info:
            params["use_locking"] = xml_info["optimizer_use_locking"]
        if "optimizer_name" in xml_info:
            params["name"] = xml_info["optimizer_name"]
        template_variables["optimizer_module"] = "tf.train"
        template_variables["optimizer_name"] = "'AdagradOptimizer'"
        template_variables["optimizer_params"] = params

    elif opt_name == "momentum":
        params = dict()
        params["learning_rate"] = learning_rate
        if "optimizer_use_locking" in xml_info:
            params["use_locking"] = xml_info["optimizer_use_locking"]
        if "optimizer_name" in xml_info:
            params["name"] = xml_info["optimizer_name"]
        template_variables["optimizer_module"] = "tf.train"
        template_variables["optimizer_name"] = "'MomentumOptimizer'"
        template_variables["optimizer_params"] = params

    elif opt_name == "adam":
        params = dict()
        params["learning_rate"] = learning_rate
        if "optimizer_beta1" in xml_info:
            params["beta1"] = xml_info["optimizer_beta1"]
        if "optimizer_beta2" in xml_info:
            params["beta2"] = xml_info["optimizer_beta2"]
        if "optimizer_epsilon" in xml_info:
            params["epsilon"] = xml_info["optimizer_epsilon"]
        if "optimizer_use_locking" in xml_info:
            params["use_locking"] = xml_info["optimizer_use_locking"]
        if "optimizer_name" in xml_info:
            params["name"] = xml_info["optimizer_name"]
        template_variables["optimizer_module"] = "tf.train"
        template_variables["optimizer_name"] = "'AdamOptimizer'"
        template_variables["optimizer_params"] = params

    elif opt_name == "ftrl":
        params = dict()
        params["learning_rate"] = learning_rate
        if "optimizer_learning_rate_power" in xml_info:
            params["learning_rate_power"] = xml_info["optimizer_learning_rate_power"]
        if "optimizer_initial_accumulator_value" in xml_info:
            params["initial_accumulator_value"] = xml_info["optimizer_initial_accumulator_value"]
        if "optimizer_l1_regularization_strength" in xml_info:
            params["l1_regularization_strength"] = xml_info["optimizer_l1_regularization_strength"]
        if "optimizer_l2_regularization_strength" in xml_info:
            params["l2_regularization_strength"] = xml_info["optimizer_l2_regularization_strength"]
        if "optimizer_use_locking" in xml_info:
            params["use_locking"] = xml_info["optimizer_use_locking"]
        if "optimizer_name" in xml_info:
            params["name"] = xml_info["optimizer_name"]
        template_variables["optimizer_module"] = "tf.train"
        template_variables["optimizer_name"] = "'FtrlOptimizer'"
        template_variables["optimizer_params"] = params

    elif opt_name == "rmsprop":
        params = dict()
        params["learning_rate"] = learning_rate
        if "optimizer_decay" in xml_info:
            params["decay"] = xml_info["optimizer_decay"]
        if "optimizer_momentum" in xml_info:
            params["momentum"] = xml_info["optimizer_momentum"]
        if "optimizer_epsilon" in xml_info:
            params["epsilon"] = xml_info["optimizer_epsilon"]
        if "optimizer_use_locking" in xml_info:
            params["use_locking"] = xml_info["optimizer_use_locking"]
        if "optimizer_name" in xml_info:
            params["name"] = xml_info["optimizer_name"]
        template_variables["optimizer_module"] = "tf.train"
        template_variables["optimizer_name"] = "'RMSPropOptimizer'"
        template_variables["optimizer_params"] = params


def parse_xml(element_id: str, parent: et.Element, node: et.Element,
              xml_info: dict):
    """
    Fill template variavle dictionary recursively
    A format of key of text field is (parenttag_currenttag)
        ex) from
            <xval>
                <low>10</low>
            </xval>
            to
            template[xval_low] = 10
    and format of attribute filed is (attribute_parenttag_currenttag)
        ex) from
            <conv_layer id = "1">
                <activation>
                    <type>relu</type>
                    <strides>
                        <vertical>1</vertical>
            to
            template[1_activation_type] = "relu"
            template[1_strides_vertical] = "1"

    :param element_id:          element id which is unique value
    :param parent:              parent node
    :param node:                current node
    :param xml_info:            xml information dictionary
    :return:                    void
    """

    key = ""
    for attr in node.attrib:
        element_id = node.attrib[attr]
    if element_id != "":
        key += element_id + "_"
    key += parent.tag
    key += "_" + node.tag
    if parent != node:
        xml_info[key] = node.text
    for child in node:
        parse_xml(element_id, node, child, xml_info)
    element_id = ""
