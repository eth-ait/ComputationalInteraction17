from keras.layers import Input, Dense, BatchNormalization, Dropout, LeakyReLU
from keras.models import Model
from keras.optimizers import RMSprop
import numpy as np
import keras.objectives

from layers.GaussianNoiseHand import GaussianNoiseHand

import matplotlib.pyplot as plt
import collections

from keras import regularizers

class AutoEncoder(object):
    def __init__(self, input_dim, coding_dims=[128, 64, 8], dropout=None, dropout_inputs=0,
                 noise=0, loss=keras.objectives.mean_squared_error, batch_size=50,
                 name_tag=None):

        self.input_dim = input_dim
        self.coding_dims = coding_dims
        self.latent_dim = coding_dims[-1]
        self.coding_depth = len(coding_dims)
        self.batch_size = batch_size

        if not isinstance(noise, collections.Sequence):
            noise = [noise, noise]
        self.noise = noise
        self.dropout = dropout
        self.dropout_inputs = dropout_inputs
        self.model_ae = None
        self.model_encoder = None
        self.model_decoder = None
        self.name_tag = name_tag
        self.model_name = self.create_model_name()

        self.history = {}
        self.untrained = True

        self.fit_verbose = True

        self.learning_rate = 0.0001

        self.reg_dense_kernel = regularizers.l2(0.0001)

        self.loss = loss
        self.setup()

    def load_from_file(self, filepath):
        """Creates and wires up the layers and sets the weights of this model as specified in the given file.
        Note that the constructor parameters of this instance have to match those of the originally stored model.
        """

        self.model_ae.load_weights(filepath) #
        # self.model_ae = load_model(filepath) # this does not work reliably with custom layers

        '''
        Note:
        After loading the model and weights, we need to set up the encoder and decoder
        manually to ensure that the keras objects are linked up properly.
        If we just save and load the encoder/decoder as well as the main model they will not
        be linked up after loading, i.e. training the main model will not influence the loaded
        encoder/decoder parts.
        Hence, it seems like a good idea to always just save/load the main model
        and to rewire the submodels after loading the main one.
        '''
        self.setup_encoder()
        self.setup_decoder()

    def save_to_file(self, path, model_name=None, verbose=False):
        """Writes this model to the given path, using the given model name as the file name.
        If no model name is given, a name will be generated automatically, reflecting the model's parameters."""

        if model_name == None:
            model_name = self.model_name

        filename = path + model_name + '.h5'
        self.model_ae.save(filename)

        if verbose:
            print 'Model written to file: %s' % filename

    def create_model_name(self):
        """Generates a name for this model that reflects the model's parameters."""
        model_name = 'model_ae_%d_' % self.input_dim
        model_name += '_'.join([str(v) for v in self.coding_dims])
        model_name += '_b%d' % self.batch_size

        if self.noise > 0:
            model_name += ('_n%.4f_%.4f' % (self.noise[0], self.noise[1])).replace('.', '')

        if self.name_tag is not None:
            model_name += '_' + self.name_tag
        return model_name

    def setup_encoder(self):
        """Creates and wires up the layers of the encoder submodel of this model."""

        '''
        For the encoder part of the model:
        - the input layer is the first layer
        - the output layer is the last encoding layer
        '''
        self.model_encoder = Model(input=self.model_ae.layers[0].input,
                                   output=self.model_ae.get_layer('encoded_drop').output)

    def setup_decoder(self):
        """Creates and wires up the layers of the decoder submodel of this model."""

        '''
        For the decoder part of the model:
        - the input layer is a layer with as many neurons as the final encoding has latent dimensions
        - the output is the chained application of the decoding layers (hence the use of the reduce function)
        '''
        inputs_encoded = Input(shape=(self.latent_dim,))

        first_decoder_layer = self.model_ae.get_layer('decoded_0')
        index_of_first_decoder_layer = self.model_ae.layers.index(first_decoder_layer)

        layers_decoder = reduce(lambda x, y: y(x),
                                self.model_ae.layers[index_of_first_decoder_layer:],
                                inputs_encoded)

        self.model_decoder = Model(inputs=inputs_encoded, outputs=layers_decoder)



    def setup(self):
        """Creates and wires up the layers of this model."""

        '1. Create overall model: Autoencoder'

        'Create the input layer:'
        inputs = self.setup_model_part_input()

        noised = self.setup_noise_layer(inputs)

        if self.dropout_inputs > 0:
            noised = Dropout(self.dropout_inputs, name="drop_input")(noised)

        # 'Create a normalisation layer:'
        norm_layer = BatchNormalization(epsilon=1e-4)(noised)

        'Create the encoding layers:'
        prev_layer = self.setup_model_part_encoder(prev_layer=norm_layer)

        'Create the decoding layers:'
        prev_layer = self.setup_model_part_decoder(prev_layer=prev_layer)

        'Create the final decoded/output layer:'
        model_outputs = self.setup_model_part_output(prev_layer)

        self.model_ae = Model(input=inputs, output=model_outputs)


        '2. Create submodel 1: Encoder'
        self.setup_encoder()

        '3. Create submodel 2: Decoder'
        self.setup_decoder()

        self.compile(None)



    def setup_model_part_encoder(self, prev_layer):

        if self.dropout is not None:
            dropouts = self.dropout
        else:
            dropouts = np.zeros(len(self.coding_dims))
        coding_layer_index = 0
        for coding_dim in self.coding_dims:
            layer_name = 'encoded'
            if coding_layer_index < self.coding_depth - 1:
                layer_name += '_' + str(coding_layer_index)
            prev_layer = Dense(coding_dim, kernel_initializer='he_uniform', name=layer_name,
                               kernel_regularizer=self.reg_dense_kernel)(prev_layer)
            prev_layer = BatchNormalization()(prev_layer)
            prev_layer = LeakyReLU(name=layer_name + '_act')(prev_layer)
            prev_layer = Dropout(dropouts[coding_layer_index], name=layer_name + '_drop')(prev_layer)
            coding_layer_index += 1
        return prev_layer

    def setup_model_part_decoder(self, prev_layer):
        if self.dropout is not None:
            dropouts = self.dropout[::-1]
        else:
            dropouts = np.zeros(len(self.coding_dims))
        coding_layer_index = 0
        for coding_dim in self.coding_dims[-2::-1]:  # -2 -> skip the bottleneck layer, -1 -> iterate backwards
            layer_name = 'decoded_' + str(coding_layer_index)
            prev_layer = Dense(coding_dim, kernel_initializer='he_uniform', name=layer_name,
                               kernel_regularizer=self.reg_dense_kernel)(prev_layer)
            prev_layer = BatchNormalization()(prev_layer)
            prev_layer = LeakyReLU(name=layer_name + '_act')(prev_layer)
            prev_layer = Dropout(dropouts[coding_layer_index], name=layer_name + '_drop')(prev_layer)
            coding_layer_index += 1
        decoded = Dense(self.input_dim, kernel_initializer='he_uniform', name='decoded', activation='linear',
                        kernel_regularizer=self.reg_dense_kernel)(prev_layer)

        return decoded

    def setup_model_part_input(self):
        return Input(shape=(self.input_dim,), name='input')

    def setup_model_part_output(self, prev_layer):
        return prev_layer

    def setup_loss(self, data):
        return self.loss

    def setup_noise_layer(self, prev_layer):
        return GaussianNoiseHand(n_dim=self.input_dim, stddev_origin=self.noise[0],
                                 stddev_quats=self.noise[1], name='input_noise')(prev_layer)

    def clear_history(self):
        self.history = {}

    def collect_history(self, history):

        for key, val in history.history.iteritems():
            if self.history.has_key(key):
                self.history[key] = np.concatenate((self.history[key], np.copy(val)))
            else:
                self.history[key] = np.copy(val)

    def compile(self, data):
        opti = RMSprop(lr=self.learning_rate)
        self.loss = self.setup_loss(data)
        self.model_ae.compile(optimizer=opti, loss=self.loss)
        if self.model_decoder is not None:
            self.model_decoder.compile(optimizer=opti, loss=self.loss)

    def call_fit(self, inputs, outputs, validation_data, sample_weights,
                 dataframe, batch_size, epochs, verbose, prefit=None):

        if prefit is not None:
            inputs, outputs, validation_data = prefit.apply(
                inputs, outputs, validation_data, dataframe, batch_size, epochs, verbose)

        if validation_data is not None and len(validation_data) != 2:
            validation_data = (validation_data, validation_data)

        return self.model_ae.fit(
            inputs,
            outputs,
            validation_data=validation_data,
            sample_weight=sample_weights,
            batch_size=batch_size,
            epochs=epochs,
            verbose=verbose)

    def train_epochs(self, data, outputs=None, validation_data=None, sample_weights=None,
                     epochs=10, repetitions=10,
                     dataframe=None, prefit=None,
                     path=None, recompile=False, clear_history=False, verbose=True):
        """Trains this model for the given number of epochs times the given number of repetitions.
        If model_storage_path (and model_name) is set, the model is saved to the given folder after each repetition.
        This method is useful to train the model for a longer time and ensure that it is regularly
        saved while doing so."""

        if outputs is None:
            outputs = data

        if clear_history:
            self.clear_history()

        if recompile or self.untrained:
            self.compile(data)
            self.untrained = False

        for repetition in xrange(repetitions):


            history = self.call_fit(
                inputs=data, outputs=outputs, validation_data=validation_data, sample_weights=sample_weights,
                prefit=prefit, dataframe=dataframe,
                batch_size=self.batch_size, epochs=epochs, verbose=self.fit_verbose)
            self.collect_history(history)

            if verbose:
                print 'Repetition %d done.' % repetition
            if path != None:
                self.save_to_file(path, verbose=verbose)

    def decode(self, data):
        preds = self.model_decoder.predict(data)
        return preds

    def encode(self, data):
        return self.model_encoder.predict(data)

    def evaluate(self, data, batch_size, verbose):
        return self.model_ae.evaluate(data, data, batch_size=batch_size, verbose=verbose)

    def plot_history(self, offset=0, save_to_path=None, hide=False):
        fig = plt.figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        for key, val in self.history.iteritems():
            ls = '-' if not 'val' in key else '--'
            plt.semilogy(val[offset:], label=key, ls=ls)

        plt.legend()
        plt.tight_layout()
        if save_to_path is not None:
            plt.savefig(save_to_path, bbox_inches='tight')
        if not hide:
            plt.show()
        else:
            del fig
