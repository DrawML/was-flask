"""
DrawML
Linear regression template file
Templates will be changed by appropriate value

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
	x_data[:, 1:col] = raw_data[:, 0:col-1]
	y_data = raw_data[:, col-1:col]

	return x_data, y_data, x_data, y_data, x_data, y_data


def load_train_data():
	data = {X: x_train, Y: y_train}
	return data


def make_model(X, W):
	reg_enable = {{reg_enable}}
	reg_lambda = {{reg_lambda}}
	model = tf.matmul(X, tf.transpose(W))
	if reg_enable is True:
		model += reg_lambda * tf.reduce_sum(tf.square(W))
	return model


def cost_function(hypothesis, Y):
	return tf.reduce_mean(tf.square(hypothesis - Y))


def make_optimizer():
	optimizer_module = {{optimizer_module}}
	optimizer_name   = {{optimizer_name}}
	optimizer_params = {{optimizer_params}}
	return getattr(optimizer_module, optimizer_name)(**optimizer_params)


def init_weights():
	weight_init_module = {{init_module}}
	weight_params      = {{init_params}}

	weight_params['shape'] = [1, len(x_train[0])]

	weight = tf.Variable(weight_init_module(**weight_params))
	return weight


def save_model():
	# save model
	save_path = "/" """" *This will be filled at .exe step """
	saver = tf.train.Saver()
	saver.save(save_path=save_path)

x_train, y_train, x_valid, y_valid, x_test, y_test = load_input()

X = tf.placeholder(tf.float32)     # X = tf.placeholder(tf.float32, [None, 784])
Y = tf.placeholder(tf.float32)     # Y = tf.placeholder(tf.float32, [None, 10])

W = init_weights()
hypothesis = make_model(X, W)

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
