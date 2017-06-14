from keras import backend as K
from keras.engine.topology import Layer


class GaussianNoiseHand(Layer):

    def __init__(self, n_dim, stddev_origin, stddev_quats, **kwargs):
        super(GaussianNoiseHand, self).__init__(**kwargs)
        self.supports_masking = True
        self.stddev_origin = stddev_origin
        self.stddev_quats = stddev_quats
        self.n_dim = n_dim
        self.n_dim_origin = 3


    def call(self, x, training=None):

        def noised():
            x_origin = x[:, 0:self.n_dim_origin]
            x_quats = x[:, self.n_dim_origin:]
            noise_origin = K.random_normal(shape=K.shape(x_origin),
                                    mean=0.,
                                    stddev=self.stddev_origin)

            noise_quats = K.random_normal(shape=K.shape(x_quats),
                                            mean=0.,
                                            stddev=self.stddev_quats)

            noise = K.concatenate((noise_origin, noise_quats), axis=-1)
            #noise = K.print_tensor(noise, "noise")
            return x + noise

        return K.in_train_phase(noised, x, training=training)

    def get_config(self):
        config = {'stddev_origin': self.stddev_origin, 'stddev_quats': self.stddev_quats}
        base_config = super(GaussianNoiseHand, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
