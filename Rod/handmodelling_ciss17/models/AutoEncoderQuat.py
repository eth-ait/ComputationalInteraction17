import numpy as np
from objectives.QuaternionLoss import QuaternionLoss
import preprocessing.Metadata as meta
from AutoEncoder import AutoEncoder
import keras.objectives

class AutoEncoderQuat(AutoEncoder):
    def __init__(self, coding_dims=[128, 64, 8], dropout=None, dropout_inputs=0,
                 noise=0, loss=keras.objectives.mean_squared_error, batch_size=50,
                 name_tag=None):

        self.loss_mode = 0
        self.loss_weight = 1
        self.distances_raw = None
        self.distances_mean = None
        input_dim = 3 + (len(meta.aalto_hand_data.columns_features))*4

        AutoEncoder.__init__(self, input_dim, coding_dims=coding_dims, dropout=dropout, dropout_inputs=dropout_inputs,
                 noise=noise, loss=loss, batch_size=batch_size,
                 name_tag=name_tag)


    def train_epochs(self, data, outputs=None, validation_data=None,  sample_weights=None,
                     epochs=10, repetitions=10,
                     dataframe=None, prefit=None,
                     path=None, recompile=False, clear_history=False, verbose=True):
        """Trains this model for the given number of epochs times the given number of repetitions.
        If model_storage_path (and model_name) is set, the model is saved to the given folder after each repetition.
        This method is useful to train the model for a longer time and ensure that it is regularly
        saved while doing so."""

        self.set_distances(data)
        data_to_fit = self.extract_non_distance_data(data)

        validation_data_to_fit = None
        if validation_data is not None:
            validation_data_to_fit = self.extract_non_distance_data(validation_data)

        super(AutoEncoderQuat, self).train_epochs(
            data_to_fit, validation_data=validation_data_to_fit,  sample_weights=sample_weights,
            epochs=epochs, repetitions=repetitions,
            dataframe=dataframe, prefit=prefit,
            path=path, recompile=recompile, clear_history=clear_history, verbose=verbose)

    def decode(self, data):
        preds = self.model_decoder.predict(data)
        return self.insert_distances(preds)

    def encode(self, data):
        self.set_distances(data)
        data_to_encode = self.extract_non_distance_data(data)
        return self.model_encoder.predict(data_to_encode)

    def evaluate(self, data, batch_size, verbose):
        data_to_use = self.extract_non_distance_data(data)
        return self.model_ae.evaluate(data_to_use, data_to_use,
                                      batch_size=batch_size, verbose=verbose)

    def test_on_batch(self, data):
        data_to_use = self.extract_non_distance_data(data)
        return self.model_ae.test_on_batch(data_to_use, data_to_use)


    def set_distances(self, data):
        del self.distances_raw
        del self.distances_mean
        self.distances_raw = data[:, (3 + 4)::5]
        self.distances_mean = np.mean(data[:, (3 + 4)::5], axis=0)


    def extract_non_distance_data(self, data):
        return data[:, self.get_non_distance_indices(data.shape[1])]

    def get_non_distance_indices(self, num_cols):
        return [0, 1, 2] + [i for i in range(3, num_cols) if i % 5 != 2]

    def insert_distances(self, preds):
        rows, cols = preds.shape
        preds_extended = np.zeros((rows, cols+self.distances_mean.shape[0]))
        preds_extended[:, self.get_non_distance_indices(cols+len(self.distances_mean))] = preds
        preds_extended[:, (3 + 4)::5] = self.distances_mean # raw vs mean distances
        return preds_extended
