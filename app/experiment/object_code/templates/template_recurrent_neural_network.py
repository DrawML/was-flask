"""
DrawML
Recurrent Neural Network template file

There is some issues in input data
and maybe save model
"""
import tensorflow as tf
import numpy as np

training_epoch  = {{training_epoch}}
x_vertical      = {{x_vertical}}
x_horizontal    = {{x_horizontal}}
y_size          = {{y_size}}
rnn_size        = {{rnn_size}}
batch_size      = {{batch_size}}
time_step_size  = {{time_step_size}}
layer_size      = {{layer_size}}


def load_input():
	raw_data = np.loadtxt('data.txt', unpack=True, dtype='float32')
	raw_data = raw_data.T
	row = len(raw_data)
	col = len(raw_data[0])

	x_data = np.ones([row, col])
	x_data[:, 1:col] = raw_data[:, 0:col - 1]
	y_data = raw_data[:, col - 1:col]

	return x_data, y_data, x_data, y_data, x_data, y_data


def load_train_data(start, end):
	data = {X: x_train[start:end], Y: y_train[start:end]}
	return data


def make_model(rnn_size: int, layer_size: int, batch_size:int, time_step_size: int):
	cell_type = {{cell_type}}
	cell_module = None
	if cell_type == 'rnn':
		cell_module = tf.nn.rnn_cell.BasicRNNCell
	elif cell_type == 'lstm':
		cell_module = tf.nn.rnn_cell.BasicLSTMCell
	elif cell_type == 'gru':
		cell_module = tf.nn.rnn_cell.GRUCell

	src_cell = cell_module(rnn_size)
	cell = tf.nn.rnn_cell.MultiRNNCell([src_cell] * layer_size)

	initial_state = tf.zeros([batch_size, cell.state_size])
	x_split = tf.split(0, time_step_size, x_train)
	outputs, last_state = tf.nn.rnn(cell, x_split, initial_state)

	# logits: list of 2D Tensors of shape [batch_size x num_decoder_symbols]
	# targets: list of 1D batch-sized int32 Tensors of the same length as logits.
	# weights: list of 1D batch-sized float-Tensors of the same length as logits.
	logits = tf.reshape(tf.concat(1, outputs), [-1, rnn_size])
	targets = tf.placeholder(tf.int32, [batch_size, time_step_size])
	targets = tf.reshape(targets, [-1])
	weights = tf.ones([time_step_size * batch_size])

	return logits, targets, weights


def cost_function(logits, targets, weights, batch_size):
	cost = tf.nn.seq2seq.sequence_loss_by_example([logits], [targets], [weights])
	cost = tf.reduce_sum(cost) / batch_size
	return cost


def make_optimizer():
	optimizer_module = {{optimizer_module}}
	optimizer_name   = {{optimizer_name}}
	optimizer_params = {{optimizer_params}}
	return getattr(optimizer_module, optimizer_name)(**optimizer_params)


def save_model():
	# save model
	save_path = "/" """" *This will be filled at .exe step """
	saver = tf.train.Saver()
	saver.save(save_path=save_path)


x_train, y_train, x_valid, y_valid, x_test, y_test = load_input()

x_train = x_train.reshape(-1, x_vertical, x_horizontal, 1)
x_test  = x_test.reshape(-1, x_vertical, x_horizontal, 1)
x_valid = x_valid.reshape(-1, x_vertical, x_horizontal, 1)

logits, targets, weights = make_model(rnn_size, layer_size, batch_size, time_step_size)

cost = cost_function(logits, targets, weights, batch_size)
optimizer = make_optimizer()
train = optimizer.minimize(cost)
predict = tf.argmax(logits, 1)

with tf.Session() as sess:
	init = tf.initialize_all_variables()
	sess.run(init)
	for _ in range(training_epoch):
		for start, end in zip(range(0, len(x_train), batch_size), range(batch_size, len(x_train)+1, batch_size)):
			train_data = load_train_data(start, end)
			sess.run(train, feed_dict=train_data)
		accuracy = sess.run(predict)
		print("step ", _ , " accuracy ", accuracy)

	# some logging codes will be added...
	save_model()
