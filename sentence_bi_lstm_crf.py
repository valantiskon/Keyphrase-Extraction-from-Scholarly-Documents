import tables  # load compressed data files
import numpy as np
import pandas as pd
# from crf import CRF
from tf2crf import CRF
# from crf_nlp_architect import CRF   ?????
from numpy import load
import tensorflow as tf
import keras.backend as K
import sequence_evaluation
import traditional_evaluation
import matplotlib.pyplot as plt
from tensorflow import constant  # used to convert array/list to a Keras Tensor
from keras.optimizers import SGD
from keras.utils import plot_model
from sklearn.metrics import f1_score
from keras.optimizers import RMSprop
from keras.models import Model, Input
from keras.callbacks import TensorBoard
from keras.callbacks import LearningRateScheduler
from keras.optimizers.schedules import ExponentialDecay, InverseTimeDecay
from keras.layers import LSTM, Embedding, Dense, TimeDistributed, Dropout, Bidirectional

pd.set_option('display.max_columns', None)

# ======================================================================================================================
# Set data generators for batch training
# ======================================================================================================================

# Set batch size, and, the train and test data size
batch_size = 1024  # set during pre-processing (set in file preprocessing.py)
train_data_size = 4147964  # 530809 [ THE NUMBER OF TRAIN SENTENCES\DOCS ]  # the total size of train data
validation_data_size = 156836  # 20000  [ THE NUMBER OF VALIDATION SENTENCES\DOCS ]  # the total size of test data
test_data_size = 156085  # 20000 SEE BELOW [ THE NUMBER OF TEST SENTENCES\DOCS ]  # the total size of test data

# Set INPUT and OUTPUT layer size
MAX_LEN = 70  # 500  # max length of abstract and title (together) (full text train set: 2763)
VECT_SIZE = 100  # the GloVe vector size
number_labels = 2  # 2 labels, keyword (KP) and Non-keyword (Non-KP)

doc_vocab = 323895  # 100003  # the vocabulary of the train dataset

print('MAX_LEN of text', MAX_LEN)
print('VECT_SIZE', VECT_SIZE)
print('VOCABULARY', doc_vocab)

# ======================================================================================================================
# Define train/test data file names
# ======================================================================================================================
'''
# [FULL ABSTRACT TEXT - train_data_size = 530809] Define the file paths and names for TRAINING data
x_train_filename = 'data\\preprocessed_data\\x_TRAIN_data_preprocessed.hdf'
y_train_filename = 'data\\preprocessed_data\\y_TRAIN_data_preprocessed.hdf'

# [FULL ABSTRACT TEXT - validation_data_size = 20000] Define the file paths and names for VALIDATION data to tune model parameters
x_validate_filename = 'data\\preprocessed_data\\x_VALIDATION_data_preprocessed.hdf'
y_validate_filename = 'data\\preprocessed_data\\y_VALIDATION_data_preprocessed.hdf'

'''
# [SENTENCES ABSTRACT TEXT - train_data_size = 4147964] Define the file paths and names for TRAINING data
x_train_filename = 'data\\preprocessed_data\\x_TRAIN_SENTENC_data_preprocessed.hdf'
y_train_filename = 'data\\preprocessed_data\\y_TRAIN_SENTENC_data_preprocessed.hdf'

# [SENTENCES ABSTRACT TEXT - validation_data_size = 156836] Define the file paths and names for VALIDATION data to tune model parameters
x_validate_filename = 'data\\preprocessed_data\\x_VALIDATION_SENTENC_data_preprocessed.hdf'
y_validate_filename = 'data\\preprocessed_data\\y_VALIDATION_SENTENC_data_preprocessed.hdf'


# ======================================================================================================================
# Define file names for TESTING-EVALUATION of the final model (GOLD sets, preprocessed document text + keyphrases)
# ======================================================================================================================

# Full abstract
'''
# [ test_data_size = 20000 ]
x_test_filename = 'data\\preprocessed_data\\x_TEST_data_preprocessed.hdf'  # kp20k
y_test_filename = 'data\\preprocessed_data\\y_TEST_data_preprocessed'
x_filename = 'data\\preprocessed_data\\x_TEST_preprocessed_TEXT'  # kp20k
y_filename = 'data\\preprocessed_data\\y_TEST_preprocessed_TEXT'  # kp20k
'''
'''
# [ test_data_size = 211 ]
x_test_filename = 'data\\preprocessed_data\\full_abstract\\x_NUS_FULL_ABSTRACT_TEST_data_preprocessed.hdf'
y_test_filename = 'data\\preprocessed_data\\full_abstract\\y_NUS_FULL_ABSTRACT_TEST_data_preprocessed'
x_filename = 'data\\preprocessed_data\\full_abstract\\x_NUS_FULL_ABSTRACT_preprocessed_TEXT'
y_filename = 'data\\preprocessed_data\\full_abstract\\y_NUS_FULL_ABSTRACT_preprocessed_TEXT'
'''
'''
# [ test_data_size = 2304 ]
x_test_filename = 'data\\preprocessed_data\\full_abstract\\x_ACM_FULL_ABSTRACT_TEST_vectors.hdf'
y_test_filename = 'data\\preprocessed_data\\full_abstract\\y_ACM_FULL_ABSTRACT_TEST_vectors'
x_filename = 'data\\preprocessed_data\\full_abstract\\x_ACM_FULL_ABSTRACT_preprocessed_TEXT'
y_filename = 'data\\preprocessed_data\\full_abstract\\y_ACM_FULL_ABSTRACT_preprocessed_TEXT'
'''

# Sentences abstract

# [ test_data_size = 156085 ]
x_test_filename = 'data\\preprocessed_data\\x_TEST_SENTENC_data_preprocessed.hdf'  # kp20k
y_test_filename = 'data\\preprocessed_data\\y_TEST_SENTENC_data_preprocessed'
x_filename = 'data\\preprocessed_data\\x_TEST_SENTENC_preprocessed_TEXT'  # kp20k
y_filename = 'data\\preprocessed_data\\y_TEST_SENTENC_preprocessed_TEXT'  # kp20k

'''
# [ test_data_size = 1673 ]
x_test_filename = 'data\\preprocessed_data\\sentence_abstract\\x_NUS_SENTEC_ABSTRACT_TEST_data_preprocessed.hdf'
y_test_filename = 'data\\preprocessed_data\\sentence_abstract\\y_NUS_SENTEC_ABSTRACT_TEST_data_preprocessed'
x_filename = 'data\\preprocessed_data\\sentence_abstract\\x_NUS_SENTEC_ABSTRACT_preprocessed_TEXT'
y_filename = 'data\\preprocessed_data\\sentence_abstract\\y_NUS_SENTEC_ABSTRACT_preprocessed_TEXT'
'''
'''
# [ test_data_size = 17486 ]
x_test_filename = 'data\\preprocessed_data\\sentence_abstract\\x_ACM_SENTENC_ABSTRACT_TEST_data_preprocessed.hdf'
y_test_filename = 'data\\preprocessed_data\\sentence_abstract\\y_ACM_SENTENC_ABSTRACT_TEST_data_preprocessed'
x_filename = 'data\\preprocessed_data\\sentence_abstract\\x_ACM_SENTENC_ABSTRACT_preprocessed_TEXT'
y_filename = 'data\\preprocessed_data\\sentence_abstract\\y_ACM_SENTENC_ABSTRACT_preprocessed_TEXT'
'''

# Sentences fulltext
'''
# [ test_data_size = 74183 ]
x_test_filename = 'data\\preprocessed_data\\sentence_fulltext\\x_NUS_SENTEC_FULLTEXT_TEST_data_preprocessed.hdf'
y_test_filename = 'data\\preprocessed_data\\sentence_fulltext\\y_NUS_SENTEC_FULLTEXT_TEST_data_preprocessed'
x_filename = 'data\\preprocessed_data\\sentence_fulltext\\x_NUS_SENTEC_FULLTEXT_preprocessed_TEXT'
y_filename = 'data\\preprocessed_data\\sentence_fulltext\\y_NUS_SENTEC_FULLTEXT_preprocessed_TEXT'
'''
'''
# [ test_data_size = 772013 ]
x_test_filename = 'data\\preprocessed_data\\sentence_fulltext\\x_ACM_SENTENC_FULLTEXT_TEST_data_preprocessed.hdf'
y_test_filename = 'data\\preprocessed_data\\sentence_fulltext\\y_ACM_SENTENC_FULLTEXT_TEST_data_preprocessed'
x_filename = 'data\\preprocessed_data\\sentence_fulltext\\x_ACM_SENTENC_FULLTEXT_preprocessed_TEXT'
y_filename = 'data\\preprocessed_data\\sentence_fulltext\\y_ACM_SENTENC_FULLTEXT_preprocessed_TEXT'
'''


# ======================================================================================================================
# Read train data
# ======================================================================================================================

def batch_generator(x_filename, y_filename, batch_size, number_of_batches):
    '''
    Continuously generates the data batches
    :param x_filename: the file name that contains pre-processed data of x
    :param y_filename: the file name that contains pre-processed data of y
    :param batch_size: the size of each batch
    :param number_of_batches: the total number of batches
    :return: yields data batches of x and y (Keras generator should not return and should continuously run)
    '''
    current_batch_number = 0  # the identifier used for each batch of data (ex. 0, 10000, 20000, 30000, etc.)

    if 'TRAIN' in x_filename:  # for training yield a batch as a dummy, because it does not read the first ever batch
        yield load_data(x_filename, y_filename, current_batch_number)  # needed to avoid loosing the first batch of data

    while True:
        yield load_data(x_filename, y_filename, current_batch_number)

        # calculate the identifier of each batch of data
        if current_batch_number < batch_size * number_of_batches:
            current_batch_number += batch_size
        else:
            current_batch_number = 0


def load_data(x_filename, y_filename, batch_number):
    '''
    Load the data batch-by-batch
    :param x_filename: the file name that contains pre-processed data of x
    :param y_filename: the file name that contains pre-processed data of y
    :param batch_number: the current number of batch for a specific iteration (ex. 2nd batch out of 10)
    :return: pre-processed data of x and y (y as tensor)
    '''

    print('batch_number', batch_number)
    print(x_filename)

    # Read X batches for testing from file (pre-processed)
    with tables.File(x_filename, 'r') as h5f:
        x = h5f.get_node('/x_data' + str(batch_number)).read()  # get a specific chunk of data
        # print(x)
    #        print('X SHAPE AFTER', np.array(x, dtype=object).shape)

    if not y_filename == '':  # for TEST data read only the x values
        # Read y batches for testing from file (pre-processed)
        with tables.File(y_filename, 'r') as h5f:
            y = h5f.get_node('/y_data' + str(batch_number)).read()  # get a specific chunk of data
            # print(y)
    #            print('y SHAPE AFTER', np.array(y, dtype=object).shape)

    '''
    print(y)
    here = [1 if doc[:, 1].any() else 0 for doc in y]
    print('y SHAPE AFTER', np.array(y, dtype=object).shape)
    if any(here):
        print('THERE ARE KEYPHRASES')
    else:
        print('THERE ARE NOOOOOOT KEYPHRASES')
    '''

    '''
    if 'TRAIN' in x_filename:  # for training return class weights as well
        """
            # FULL ABSTRACT
            KP count:  3876504 
            NON-KP count:  79634175

            # SENTENCES
            KP count:  3873971 
            NON-KP count:  79557044
        """
        # The weight of label 0 (Non-KP) is 1 and the weight of class 1 (KP) is the number of occurences of class 0 (79634175 / 3883863 = 20.54)
        sample_weights = [[1 if label[0] else 20.54 for label in instance] for instance in y]  # shape (1024, 3022)
        print('class_weights', np.array(sample_weights, dtype=float).shape)
        return x, constant(y), np.array(sample_weights, dtype=float)  # (inputs, targets, sample_weights)
    '''
    if y_filename == '':  # for TEST data return only the x values
        return x

    return x, constant(y)


# USE weights for all data? (train, validation and test???)


# ======================================================================================================================
# Set data generators for batch training/validation/prediction
# ======================================================================================================================

# ceil of the scalar x is THE SMALLER INTEGER i, such that i >= x
steps_per_epoch = np.ceil(train_data_size / batch_size)  # number of training batches
validation_steps = np.ceil(validation_data_size / batch_size)  # number of validation and testing batches (same size)
test_steps = np.ceil(test_data_size / batch_size)  # number of validation and testing batches (same size)
print('steps_per_epoch', steps_per_epoch)
print('validation_steps', validation_steps)
print('test_steps', test_steps)

# (number of batches) -1, because batches start from 0
training_batch_generator = batch_generator(x_train_filename, y_train_filename, batch_size, steps_per_epoch - 1)  # training batch generator
validation_batch_generator = batch_generator(x_validate_filename, y_validate_filename, batch_size, validation_steps - 1)  # validation batch generator
test_batch_generator = batch_generator(x_test_filename, '', batch_size, test_steps - 1)  # testing batch generator

# ======================================================================================================================
# Define f1-score to monitor during training and save the best model with Checkpoint
# ======================================================================================================================
'''
def f1score(y_true, y_predicted):  # taken from old keras source code
    true_positives = K.sum(K.round(K.clip(y_true * y_predicted, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_predicted, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    recall = true_positives / (possible_positives + K.epsilon())
    f1_val = 2*(precision*recall)/(precision+recall+K.epsilon())
    return f1_val
'''

'''
def create_f1():
    def f1_function(y_true, y_pred):
        y_pred_binary = tf.where(y_pred>=0.5, 1., 0.)
        y_true = tf.cast(y_true, tf.float32)
        tp = tf.reduce_sum(y_true * y_pred_binary)
        predicted_positives = tf.reduce_sum(y_pred_binary)
        possible_positives = tf.reduce_sum(y_true)
        return tp, predicted_positives, possible_positives
    return f1_function


class f1score(keras.metrics.Metric):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # handles base args (e.g., dtype)
        self.f1_function = create_f1()
        self.tp_count = self.add_weight("tp_count", initializer="zeros")
        self.all_predicted_positives = self.add_weight('all_predicted_positives', initializer='zeros')
        self.all_possible_positives = self.add_weight('all_possible_positives', initializer='zeros')

    def update_state(self, y_true, y_pred, sample_weight=None):
        tp, predicted_positives, possible_positives = self.f1_function(y_true, y_pred)
        self.tp_count.assign_add(tp)
        self.all_predicted_positives.assign_add(predicted_positives)
        self.all_possible_positives.assign_add(possible_positives)

    def result(self):
        precision = self.tp_count / self.all_predicted_positives
        recall = self.tp_count / self.all_possible_positives
        f1 = 2*(precision*recall)/(precision+recall)
        return f1
'''


def load_y_test(y_file_name, batch_size, number_of_batches):
    """
    Load y_test for validation
    :param y_file_name: the file name that contains pre-processed data of y_test
    :param batch_size: the size of each batch
    :param number_of_batches: the total number of batches
    :return: return y_test (y_test_flat) for validation
    """
    y_test_batches = []  # save y_test for validation
    current_batch_number = 0  # the identifier used for each batch of data (ex. 0, 10000, 20000, 30000, etc.)
    while True:
        # Read X batches for testing from file (pre-processed)
        with tables.File(y_file_name, 'r') as h5f:
            y_test_batches.append(
                h5f.get_node('/y_data' + str(current_batch_number)).read())  # get a specific chunk of data

        # calculate the identifier of each batch of data
        if current_batch_number < batch_size * number_of_batches:
            current_batch_number += batch_size
        else:
            y_test_flat = [y_label for y_batch in y_test_batches for y_label in
                           y_batch]  # flatten the y_test (20000, 2881, 2)
            print('y_test SHAPE AFTER', np.array(y_test_flat, dtype=object).shape)
            return y_test_flat


def pred2label(all_abstract_preds):
    '''
    Converts prediction set and test/validation set from two columns (one for each label value)
    to just one column with the number of the corresponding label
    [ initial array: [1, 0] => final array: [0] ]   -   [ initial array: [0, 1] => final array: [1] ]
    :param all_abstract_preds: array with predictions or test/validation set [documents/abstracts, number of words]
    :return: flattened array that contains the prediction for each word [number of total words of all abstracts]
    '''
    preds = []
    for abstract_preds in all_abstract_preds:
        for word_pred in abstract_preds:
            # the position of the max value is corresponding to the actual label value (0: Non-KP, 1: KP)
            preds.append(np.argmax(word_pred))
    return preds


y_test = load_y_test(y_validate_filename, batch_size, validation_steps - 1)  # load y_test in memory
y_test = pred2label(y_test)  # convert y_test from categorical (two columns, 1 for each label) to a single value label


class PredictionCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        y_pred = self.model.predict(x=validation_batch_generator, steps=validation_steps)  # steps=validation_steps, because it does not read the last batch
        y_pred = pred2label(y_pred)  # convert y_test from categorical (two columns, 1 for each label) to a single value label
        # print("Epoch: {} F1-score: {:.2%}".format(epoch, f1_score(y_test, y_pred, pos_label=1)))
        logs.update({'val_f1score': f1_score(y_test, y_pred, pos_label=1)})
        #     logs['val_f1score'] = f1_score(y_test, y_pred, pos_label=1)
        super().on_epoch_end(epoch, logs)


# ======================================================================================================================
# Load GloVe embedding
# ======================================================================================================================

# load dict of arrays
dict_data = load('data\\embedding_matrix.npz')
# extract the first array
embedding_matrix = dict_data['arr_0']
# print the array
print(embedding_matrix)

# ======================================================================================================================
# Bi-LSTM-CRF
# ======================================================================================================================

# Model definition
inpt = Input(shape=(MAX_LEN,))  # MAX_LEN, VECT_SIZE
# input_dim: Size of the vocabulary, i.e. maximum integer index + 1
# output_dim: Dimension of the dense embedding
# input_shape: 2D tensor with shape (batch_size, input_length)

# doc_vocab: vocabulary - number of words - of the train dataset
model = Embedding(doc_vocab, output_dim=100, input_length=MAX_LEN,  # n_words + 2 (PAD & UNK)
                  weights=[embedding_matrix],  # use GloVe vectors as initial weights
                  mask_zero=True, trainable=True)(inpt)  # name='word_embedding'

# recurrent_dropout=0.1 (recurrent_dropout: 10% possibility to drop of the connections that simulate LSTM memory cells)
# units = 100 / 0.55 = 182 neurons (to account for 0.55 dropout)
model = Bidirectional(LSTM(units=100, return_sequences=True))(model)  # input_shape=(1, MAX_LEN, VECT_SIZE)
model = Dropout(0.3)(model)  # 0.5
# model = TimeDistributed(Dense(number_labels, activation="relu"))(model)  # a dense layer as suggested by neuralNer
model = Dense(number_labels, activation=None)(model)  # activation='linear' (they are the same)
crf = CRF(number_labels)  # CRF layer { SHOULD I SET -> number_labels+1 (+1 -> PAD) }
out = crf(model)  # output
model = Model(inputs=inpt, outputs=out)


# set learning rate
# lr_rate = InverseTimeDecay(initial_learning_rate=0.05, decay_rate=4, decay_steps=steps_per_epoch)
# lr_rate = ExponentialDecay(initial_learning_rate=0.01, decay_rate=0.5, decay_steps=10000)


# learning rate schedule
def step_decay(epoch):
    initial_lrate = 0.01
    drop = 0.5
    # epochs_drop = 1.0  # how often to change the learning rate
    lrate = initial_lrate / (1 + drop * epoch)
    # print('epoch:', epoch, 'lrate:', lrate)
    '''
    lrate=[0.01, 0.0075, 0.005, 0.0025, 0.001]
    lrate = lrate[epoch]
    '''
    return lrate


lrate = LearningRateScheduler(step_decay)

# 2 F1-score: 0.2080 + 30 + 0.22
# 3 F1-score: 0.1821 + 0.16

# set optimizer
# decay=learning_rate / epochs
# CASE 1: decay=0.01
# CASE 2: decay=0.1/5
opt = SGD(learning_rate=0.0, momentum=0.9, clipvalue=5.0)  # clipvalue (Gradient Clipping): clip the gradient to [-5 to 5]
# opt = SGD(learning_rate=0.05, decay=0.01, momentum=0.9, clipvalue=3.0, clipnorm=1.0)  # clipvalue (Gradient Clipping): clip the gradient to [-5 to 5]
# opt = SGD(learning_rate=lr_rate, clipvalue=3.0, clipnorm=2.0, momentum=0.9)  # clipvalue (Gradient Clipping): clip the gradient to [-5 to 5]

# compile Bi-LSTM-CRF
model.compile(optimizer=opt, loss=crf.loss, metrics=[crf.accuracy])  # , f1score()
# model.compile(optimizer=opt, loss=crf.loss, metrics=[crf.viterbi_accuracy])

print('BEFORE TRAINING', model.get_weights())


# ======================================================================================================================
# Model Training
# ======================================================================================================================

# Track and report learning rate
class LRTensorBoard(TensorBoard):
    def __init__(self, log_dir, **kwargs):  # add other arguments to __init__ if you need
        super().__init__(log_dir=log_dir, **kwargs)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        optimizer = self.model.optimizer
        lr = K.eval(tf.cast(optimizer.lr, dtype=tf.float32) * (1. / (1. + tf.cast(optimizer.decay, dtype=tf.float32) * tf.cast(optimizer.iterations, dtype=tf.float32))))
        logs.update({'lr-SGD': lr})
        super().on_epoch_end(epoch, logs)


my_callbacks = [
    lrate,  # learning rate scheduler
    # save the weights of the model with the best f1-score after each epoch
    tf.keras.callbacks.ModelCheckpoint(filepath='pretrained_modelss\\checkpoint\\model.{epoch:02d}.h5',
                                       # -{val_f1score:.2f}   val_loss
                                       save_weights_only=True,
                                       #       monitor='val_f1score',  # val_loss
                                       #       mode='max',  # min
                                       save_best_only=False),
    LRTensorBoard(log_dir="/tmp/tb_log"),  # report learning rate after each epoch
    PredictionCallback()
]

# tf.keras.callbacks.TensorBoard(log_dir='./logs')
# tensorboard --logdir logs/validation         [ USE ON TERMINAL ]


# Train model
history = model.fit(x=training_batch_generator, steps_per_epoch=steps_per_epoch,
                    validation_data=validation_batch_generator, validation_steps=validation_steps - 1,
                    # -1, because it reads more times than actual needed
                    epochs=5, callbacks=my_callbacks, verbose=2)

# [MANDATORY] Convert data to either a Tensorflow tensor (for CRF layer) or a numpy array
# y_train = constant(y_train)  # convert array/list to a Keras Tensor
# y_train = np.array(y_train)  # convert array/list to a numpy array

model.summary()

print('AFTER TRAINING', model.get_weights())

# ======================================================================================================================
# Track model loss per epoch
# ======================================================================================================================

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
# plt.show()
plt.savefig('pretrained_modelss\\model_loss_per_epoch.png')  # save the plot of model's loss per epoch to file

# ======================================================================================================================
# Predict on validation data
# ======================================================================================================================

print('\nPredicting...')
y_pred = model.predict(x=test_batch_generator, steps=test_steps)  # steps=validation_steps, because it does not read the last batch
print(y_pred)
print('\nY_PRED SHAPE', np.array(y_pred, dtype=object).shape)

# ======================================================================================================================
# Evaluation
# ======================================================================================================================

# traditional evaluation the model's performance
traditional_evaluation.evaluation(y_pred, x_filename, y_filename)

# sequence evaluation of the model's performance
sequence_evaluation.evaluation(y_pred, MAX_LEN, y_test_filename)

print('f1-score after each epoch: ', history.history['val_f1score'])
print('learning rate after each epoch: ', history.history['lr'])

# ======================================================================================================================
# Model Saving
# ======================================================================================================================

# Save the model (weights)
# save_all_weights | load_all_weights: saves model and optimizer weights (save_weights and save)
model.save_weights("pretrained_modelss\\fulltext_model_weights.h5")  # sentences_model_weights.h5

'''
# `assert_consumed` can be used as validation that all variable values have been restored from the checkpoint. 
# See `tf.train.Checkpoint.restore` for other methods in the Status object.
print(load_status.assert_consumed())

# Check that all of the pretrained weights have been loaded.
for a, b in zip(pretrained.weights, model.weights):
    np.testing.assert_allclose(a.numpy(), b.numpy())
'''

# Save the model (architecture, loss, metrics, optimizer state, weights)
model.save('pretrained_modelss\\fulltext_bi_lstm_crf_dense_linear.h5')  # sentences_bi_lstm_crf_dense_linear.h5
'''
# Load the model
from keras.models import load_model
model = load_model('pretrained_modelss\\fulltext_bi_lstm_crf_dense_linear.h5', custom_objects={'CRF': CRF(number_labels), 'num_classes': number_labels})  #  , 'loss': crf.loss, 'metrics': [crf.accuracy]
'''

# ======================================================================================================================
# Plot the layer architecture of LSTM
# ======================================================================================================================

plot_model(model, "schemas\\sent_bi-lstm-crf_architecture.png", show_shapes=True)
