"""
DrawML
Neural Network template file

There is some issues in input data
and maybe save model
"""
import tensorflow as tf
import numpy as np

training_epoch = {{training_epoch}}


def load_input():
	raw_data = np.loadtxt('data.txt', unpack=True, dtype='float32')
	raw_data = raw_data.T
	row = len(raw_data)
	col = len(raw_data[0])

	x_data = np.ones([row, col])
	x_data[:, 1:col] = raw_data[:, 0:col - 1]
	y_data = raw_data[:, col - 1:col]

	return x_data, y_data, x_data, y_data, x_data, y_data


def load_train_data():
	data = {X: x_train, Y: y_train}
	return data


def make_activation(src: str):
	src_split = src.split('.')
	module = None
	for i in range(len(src_split)):
		if i == 0:
			module = globals()[src_split[i]]
		else:
			module = getattr(module, src_split[i])
	return module


def make_model(X, W, B):
	layers = [X];
	activation_functions = {{activation_functions}}
	for i in range(len(W)-1):
		activ_func = make_activation(activation_functions[i])
		layer_temp = tf.add(tf.matmul(layers[i], W[i]), B[i])
		layer = activ_func(layer_temp)
		layers.append(layer)

	size = len(W)
	model = tf.add(tf.matmul(layers[size-1], W[size-1]), B[size-1])

	""" next 4 lines are for regularization.
		And They have to change
	reg_enable = {{reg_enable}}
	reg_lambda = {{reg_lambda}}
	if reg_enable is True:
		 model += (reg_lambda / 2) * tf.reduce_mean(tf.reduce_sum(tf.square(W)))
	"""
	return model


def cost_function(hypothesis, Y):
	return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(hypothesis, Y))

def make_optimizer():
	optimizer_module = {{optimizer_module}}
	optimizer_name   = {{optimizer_name}}
	optimizer_params = {{optimizer_params}}
	return getattr(optimizer_module, optimizer_name)(**optimizer_params)


def init_weights():
	W = []
	B = []
	weight_init_module = {{init_module}}
	weight_params = {{init_params}}
	layer_size = {{layer_size}}
	input_shape = {{input_shape}}
	output_shape = {{output_shape}}
	{% for i in range(layer_size) %}

	weight_params['shape'] = [input_shape[{{i}}], output_shape[{{i}}]]
	W.append(tf.Variable(weight_init_module(**weight_params)))
	weight_params['shape'] = [output_shape[{{i}}]]
	B.append(tf.Variable(weight_init_module(**weight_params)))
	{% endfor %}

	return W, B


def save_model():
	# save model
	save_path = "/" """" *This will be filled at .exe step """
	saver = tf.train.Saver()
	saver.save(save_path=save_path)


x_train, y_train, x_valid, y_valid, x_test, y_test = load_input()

X = tf.placeholder(tf.float32, [None, len(x_train[0])])
Y = tf.placeholder(tf.float32, [None, len(y_train[0])])

W, B = init_weights()
hypothesis = make_model(X, W, B)

cost = cost_function(hypothesis, Y)
optimizer = make_optimizer()
train = optimizer.minimize(cost)

with tf.Session() as sess:
	init = tf.initialize_all_variables()
	sess.run(init)
	train_data = load_train_data()
	for _ in range(training_epoch):
		sess.run(train, feed_dict=train_data)
		# some logging codes will be added...
	save_model()
