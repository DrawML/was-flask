"""
DrawML
Neural Network template file

There is some issues in input data
and maybe save model

test with mnist
"""
import tensorflow as tf
import numpy as np
import sys
import os

training_epoch = 1024

SAVE_PATH = '/Users/chan/test/trained_model'

def load_input():
	argc = len(sys.argv)
	if argc < 2:
		print('No input argument')
		sys.exit(2)

	file_path = sys.argv[1]
	if os.path.isfile(file_path) is False:
		print('No such file or directory', file_path)
		sys.exit(2)

	x = np.genfromtxt(file_path, max_rows=1)
	raw_data = np.genfromtxt(file_path, dtype='float32', skip_header=1)

	feature_size    = int(x[0])
	label_size      = int(x[1])

	x_data = raw_data[:, 0:feature_size]
	y_data = raw_data[:, feature_size:feature_size+label_size]

	return x_data, y_data, x_data, y_data, x_data, y_data


def make_optimizer():
	optimizer_module = tf.train
	optimizer_name   = 'GradientDescentOptimizer'
	optimizer_params = {'learning_rate': 0.01}
	return getattr(optimizer_module, optimizer_name)(**optimizer_params)


def save_model(sess, path):
	saver = tf.train.Saver()
	saver.save(sess, path)


def restore_model(sess, path):
	saver = tf.train.Saver()
	saver.restore(sess, path)


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
	layers = [X]
	activation_functions = ['tf.nn.relu', 'tf.nn.relu', 'tf.nn.relu']
	for i in range(len(W)-1):
		activ_func = make_activation(activation_functions[i])
		layer_temp = tf.add(tf.matmul(layers[i], W[i]), B[i])
		layer = activ_func(layer_temp)
		layers.append(layer)

	size = len(W)
	model = tf.add(tf.matmul(layers[size-1], W[size-1]), B[size-1])

	""" next 4 lines are for regularization.
		And They have to change
	reg_enable = True
	reg_lambda = 0.0
	if reg_enable is True:
		 model += (reg_lambda / 2) * tf.reduce_mean(tf.reduce_sum(tf.square(W)))
	"""
	return model


def cost_function(hypothesis, Y):
	return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(hypothesis, Y))


def init_weights():
	W = []
	B = []
	weight_init_module = tf.random_uniform
	weight_params = {'maxval': 1.0, 'minval': -1.0}
	layer_size = 3
	input_shape = [784, 256, 256]
	output_shape = [256, 256, 10]
	
	weight_params['shape'] = [input_shape[0], output_shape[0]]
	W.append(tf.Variable(weight_init_module(**weight_params)))
	weight_params['shape'] = [output_shape[0]]
	B.append(tf.Variable(weight_init_module(**weight_params)))
	
	weight_params['shape'] = [input_shape[1], output_shape[1]]
	W.append(tf.Variable(weight_init_module(**weight_params)))
	weight_params['shape'] = [output_shape[1]]
	B.append(tf.Variable(weight_init_module(**weight_params)))
	
	weight_params['shape'] = [input_shape[2], output_shape[2]]
	W.append(tf.Variable(weight_init_module(**weight_params)))
	weight_params['shape'] = [output_shape[2]]
	B.append(tf.Variable(weight_init_module(**weight_params)))
	
	return W, B


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

	# training cycle
	for epoch in range(training_epoch):
		avg_cost = 0.0
		total_batch = 1000
		# loop over all batch
		sess.run(train, feed_dict={X : x_train, Y : y_train})
		# compute average loss
		avg_cost += sess.run(cost, feed_dict={X : x_train, Y : y_train}) / total_batch

		# display logs per epoch step
		if epoch % 10 == 0:
			print("Epoch : "," %04d" % (epoch+1), "Accuracy = ", "{:.9f}".format(1 - avg_cost))

	print(" Optimization Finished" )

	correct_prediction = tf.equal(tf.argmax(hypothesis, 1), tf.argmax(Y, 1))
	accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
	print("Accuracy : ", accuracy.eval(session=sess, feed_dict={X : x_train, Y : y_train}))