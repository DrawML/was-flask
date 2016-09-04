"""
DrawML
Convolution Neural Network template file

There is some issues in input data
and maybe save model

test with mnist
"""
import tensorflow as tf
import numpy as np
import sys
import os

training_epoch = 1024
dropout_conv   = 0.8
dropout_hidden = 0.8
x_vertical     = 28
x_horizontal   = 28
y_size         = 10

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
	optimizer_name   = 'RMSPropOptimizer'
	optimizer_params = {'learning_rate': 0.001}
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


def no_module(param):
	return param

def make_module(src: str):
	module = no_module
	if src == 'none':
		return module

	src_split = src.split('.')
	for i in range(len(src_split)):
		if i == 0:
			module = globals()[src_split[i]]
		else:
			module = getattr(module, src_split[i])
	return module


def make_model(X, W):
	prev_layer = X

		
	activ_func = tf.nn.relu
	pooling = tf.nn.max_pool

	l = tf.nn.conv2d(prev_layer, W['w1'],
				 strides=[1, 1, 1, 1],
				 padding='SAME')
	l = activ_func(l)
	l = pooling(l, ksize=[1, 2, 2, 1],
				strides=[1, 2, 2, 1],
				padding='SAME')
	l = tf.nn.dropout(l, p_keep_conv)
	prev_layer = l
					
	activ_func = tf.nn.relu
	pooling = tf.nn.max_pool

	l = tf.nn.conv2d(prev_layer, W['w2'],
				 strides=[1, 1, 1, 1],
				 padding='SAME')
	l = activ_func(l)
	l = pooling(l, ksize=[1, 2, 2, 1],
				strides=[1, 2, 2, 1],
				padding='SAME')
	l = tf.nn.dropout(l, p_keep_conv)
	prev_layer = l
					
	activ_func = tf.nn.relu
	pooling = tf.nn.max_pool

	l = tf.nn.conv2d(prev_layer, W['w3'],
				 strides=[1, 1, 1, 1],
				 padding='SAME')
	l = activ_func(l)
	l = pooling(l, ksize=[1, 2, 2, 1],
				strides=[1, 2, 2, 1],
				padding='SAME')
	l = tf.nn.dropout(l, p_keep_conv)
	prev_layer = l
						
	weight = W['w4']
	prev_layer = tf.reshape(prev_layer, [-1, weight.get_shape().as_list()[0]])
	activ_func = tf.nn.relu
	l = activ_func(tf.matmul(prev_layer, weight))
	l = tf.nn.dropout(l, p_keep_hidden)
	prev_layer = l
						
	weight = W['w5']
	prev_layer = tf.reshape(prev_layer, [-1, weight.get_shape().as_list()[0]])
	activ_func = no_module
	l = activ_func(tf.matmul(prev_layer, weight))
	prev_layer = l
		
	model = prev_layer
	return model


def cost_function(hypothesis, Y):
	return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(hypothesis, Y))


def init_weights():
	W = {}
	weight_init_module = tf.random_normal
	weight_params = {'stddev': 0.01}
	layers = [{'pooling_strides_v': 2, 'input_z': 1, 'input_y': 3, 'input_x': 3, 'activ_func': 'tf.nn.relu', 'activ_strides_h': 1, 'output': 32, 'activ_strides_v': 1, 'activ_padding': "'SAME'", 'num': 1, 'type': 'conv', 'pooling': 'tf.nn.max_pool', 'pooling_padding': "'SAME'", 'pooling_strides_h': 2}, {'pooling_strides_v': 2, 'input_z': 32, 'input_y': 3, 'input_x': 3, 'activ_func': 'tf.nn.relu', 'activ_strides_h': 1, 'output': 64, 'activ_strides_v': 1, 'activ_padding': "'SAME'", 'num': 2, 'type': 'conv', 'pooling': 'tf.nn.max_pool', 'pooling_padding': "'SAME'", 'pooling_strides_h': 2}, {'pooling_strides_v': 2, 'input_z': 64, 'input_y': 3, 'input_x': 3, 'activ_func': 'tf.nn.relu', 'activ_strides_h': 1, 'output': 128, 'activ_strides_v': 1, 'activ_padding': "'SAME'", 'num': 3, 'type': 'conv', 'pooling': 'tf.nn.max_pool', 'pooling_padding': "'SAME'", 'pooling_strides_h': 2}, {'num': 4, 'activ_func': 'tf.nn.relu', 'type': 'none', 'output': 625, 'input': 2048}, {'num': 5, 'activ_func': 'no_module', 'type': 'out', 'output': 10, 'input': 625}]
		
	shape = [3, 3, 1, 32]
	weight_params['shape'] = shape
	W['w1'] = tf.Variable(weight_init_module(**weight_params))
				
	shape = [3, 3, 32, 64]
	weight_params['shape'] = shape
	W['w2'] = tf.Variable(weight_init_module(**weight_params))
				
	shape = [3, 3, 64, 128]
	weight_params['shape'] = shape
	W['w3'] = tf.Variable(weight_init_module(**weight_params))
					
	shape = [2048, 625]
	weight_params['shape'] = shape
	W['w4'] = tf.Variable(weight_init_module(**weight_params))
				
	shape = [625, 10]
	weight_params['shape'] = shape
	W['w5'] = tf.Variable(weight_init_module(**weight_params))
		
	return W


x_train, y_train, x_valid, y_valid, x_test, y_test = load_input()

x_train = x_train.reshape(-1, x_vertical, x_horizontal, 1)
x_test  = x_test.reshape(-1, x_vertical, x_horizontal, 1)
x_valid = x_valid.reshape(-1, x_vertical, x_horizontal, 1)

X = tf.placeholder(tf.float32, [None, x_vertical, x_horizontal, 1])
Y = tf.placeholder(tf.float32, [None, len(y_train[0])])
p_keep_conv = tf.placeholder(tf.float32)
p_keep_hidden = tf.placeholder(tf.float32)

W = init_weights()
hypothesis = make_model(X, W)

cost = cost_function(hypothesis, Y)
optimizer = make_optimizer()
train = optimizer.minimize(cost)
predict = tf.argmax(hypothesis, 1)

with tf.Session() as sess:
	tf.initialize_all_variables().run()

	batch_size = 100
	for i in range(100):
		training_batch = zip(range(0, len(x_train), batch_size), range(batch_size, len(x_train), batch_size))
		for start, end in training_batch:
			sess.run(train, feed_dict={X: x_train[start:end], Y: y_train[start:end], p_keep_conv: 0.8, p_keep_hidden: 0.5})

		test_indices = np.arange(len(x_train)) # Get A Test Batch
		np.random.shuffle(test_indices)
		test_indices = test_indices[0:200]

		print(i, np.mean(np.argmax(y_train[test_indices], axis=1) ==
						 sess.run(predict, feed_dict={X: x_train[test_indices],
														 Y: y_train[test_indices],
														 p_keep_conv: 1.0,
														 p_keep_hidden: 1.0})))