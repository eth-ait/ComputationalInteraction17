from keras import backend as K
import numpy as np



class QuaternionLossTS(object):


    def __init__(self, input_dim=103, ts=1):
        self.input_dim = input_dim
        self.columns_origin = [0,1,2]
        self.columns_quats = [i for i in range(3, self.input_dim)]
        self.num_bones = len(self.columns_quats)/4
        self.ts = ts

    def loss(self, y_true, y_pred):
        """Custom loss function for quaternion and distance based representations of the hand.
        This implementation makes several assumptions about the order of the columns:
            - columns 0,1,2 are x,y,z of the origin of the hand.
            - columns 7,12,17 etc. are the distances (i.e. lengths of the bones)
            - columns 3,4,5,6, 8,9,10,11, etc. are the quaternion elements of the joints"""

        #y_pred = K.print_tensor(y_pred, "y_pred")


        '1. Loss for the origin location of the hand (L2):'
        # the first three columns are origin x,y,z of the hand:
        origin_loss = K.mean(K.square(y_true[:, :, self.columns_origin] - y_pred[:, :, self.columns_origin]), axis=-1)

        '2. Loss for the quaternion columns (angle and magnitude):'
        # after the origin columns every column that is not a fifth column is part of a quaternion:
        quat_loss = angle_and_mag_loss_TS(
            y_true[:, :, self.columns_quats],
            y_pred[:, :, self.columns_quats],
            self.num_bones, self.ts)

        #quat_loss *= K.mean(K.square(y_true[:, self.columns_quats] - y_pred[:, self.columns_quats]), axis=-1)

        #origin_loss = K.print_tensor(origin_loss, "origin_loss")

        return origin_loss + quat_loss
        #return K.mean(K.square(y_true[:, self.columns_quats] - y_pred[:, self.columns_quats]), axis=-1)


def angle_and_mag_loss_TS(y_true, y_pred, num_bones=25, ts=1):

    y_true += 1e-16
    y_pred += 1e-16

    y_true = K.reshape(y_true, (-1, ts, num_bones, 4))
    y_pred = K.reshape(y_pred, (-1, ts, num_bones, 4))


    mag_true = K.sqrt(helper_batch_bones_dot(y_true, y_true))
    mag_pred = K.sqrt(helper_batch_bones_dot(y_pred, y_pred))

    mag_loss = K.sum(K.square(mag_true - mag_pred), axis=-1)

    mag_true_ts_fix = K.stack((mag_true,mag_true,mag_true,mag_true))
    mag_pred_ts_fix = K.stack((mag_pred, mag_pred, mag_pred, mag_pred))
    mag_true = K.permute_dimensions(mag_true_ts_fix, [1, 2, 3, 0])
    mag_pred = K.permute_dimensions(mag_pred_ts_fix, [1, 2, 3, 0])


    y_true = y_true / mag_true
    y_pred = y_pred / mag_pred
    val = helper_batch_bones_dot(y_true, y_pred)

    #mag_val = K.sqrt(helper_batch_bones_dot(val, val))
    #mag_val = K.reshape(K.repeat_elements(mag_val, 25, -1), (-1, 25))
    #val = val / mag_val
    val = K.clip(val, -.9999999, .9999999)
    angle_loss = 2*K.sum(K.T.arccos(val), axis=-1)

    #mag_loss = K.print_tensor(mag_loss, "mag_loss")
    #angle_loss = K.print_tensor(angle_loss, "angle_loss")

    loss = mag_loss + angle_loss

    return loss


class QuaternionLoss(object):


    def __init__(self, input_dim=103):
        self.input_dim = input_dim
        self.columns_origin = [0,1,2]
        self.columns_quats = [i for i in range(3, self.input_dim)]
        self.num_bones = len(self.columns_quats)/4

    def loss(self, y_true, y_pred):
        """Custom loss function for quaternion and distance based representations of the hand.
        This implementation makes several assumptions about the order of the columns:
            - columns 0,1,2 are x,y,z of the origin of the hand.
            - columns 7,12,17 etc. are the distances (i.e. lengths of the bones)
            - columns 3,4,5,6, 8,9,10,11, etc. are the quaternion elements of the joints"""


        '1. Loss for the origin location of the hand (L2):'
        # the first three columns are origin x,y,z of the hand:
        origin_loss = K.mean(K.square(y_true[:, self.columns_origin] - y_pred[:, self.columns_origin]), axis=-1)

        '2. Loss for the quaternion columns (angle and magnitude):'
        # after the origin columns every column that is not a fifth column is part of a quaternion:
        quat_loss = angle_and_mag_loss(
            y_true[:, self.columns_quats],
            y_pred[:, self.columns_quats],
            self.num_bones)

        return origin_loss + quat_loss


def helper_batch_bones_dot(a, b):
    return K.sum(a * b, axis=-1)




def angle_and_mag_loss_variant(y_true, y_pred):

    #y_true += 1e-16
    #y_pred += 1e-16

    y_true = K.reshape(y_true, (-1, 25, 4))
    y_pred = K.reshape(y_pred, (-1, 25, 4))


    mag_true = K.sqrt(helper_batch_bones_dot(y_true, y_true))
    mag_pred = K.sqrt(helper_batch_bones_dot(y_pred, y_pred))

    mag_loss = K.sum(K.square(mag_true - mag_pred), axis=-1)

    mag_true = K.permute_dimensions(K.repeat(mag_true, 4), [0, 2, 1])
    mag_pred = K.permute_dimensions(K.repeat(mag_pred, 4), [0, 2, 1])


    y_true = y_true / mag_true
    y_pred = y_pred / mag_pred

    val = helper_batch_bones_dot(y_true, y_pred)
    val = 2*K.pow(val,2)-1
    val = K.clip(val, -.9999999, .9999999)
    angle_loss = K.sum(K.T.arccos(val), axis=-1)

    loss = mag_loss + angle_loss

    return loss



def angle_and_mag_loss(y_true, y_pred, num_bones=25):

    y_true += 1e-16
    y_pred += 1e-16

    y_true = K.reshape(y_true, (-1, num_bones, 4))
    y_pred = K.reshape(y_pred, (-1, num_bones, 4))


    mag_true = K.sqrt(helper_batch_bones_dot(y_true, y_true))
    mag_pred = K.sqrt(helper_batch_bones_dot(y_pred, y_pred))

    mag_loss = K.sum(K.square(mag_true - mag_pred), axis=-1)

    mag_true = K.permute_dimensions(K.repeat(mag_true, 4), [0, 2, 1])
    mag_pred = K.permute_dimensions(K.repeat(mag_pred, 4), [0, 2, 1])


    y_true = y_true / mag_true
    y_pred = y_pred / mag_pred
    val = helper_batch_bones_dot(y_true, y_pred)
    #mag_val = K.sqrt(helper_batch_bones_dot(val, val))
    #mag_val = K.reshape(K.repeat_elements(mag_val, 25, -1), (-1, 25))
    #val = val / mag_val
    val = K.clip(val, -.9999999, .9999999)
    angle_loss = 2*K.sum(K.T.arccos(val), axis=-1)

    #mag_loss = K.print_tensor(mag_loss, "mag_loss")
    #angle_loss = K.print_tensor(angle_loss, "angle_loss")

    loss = mag_loss + angle_loss

    return loss


def angle_and_mag_loss_old(y_true, y_pred):
    y_true += 1e-16
    y_pred += 1e-16
    mag_true = K.sqrt(K.batch_dot(y_true, y_true, axes=1))
    mag_pred = K.sqrt(K.batch_dot(y_pred, y_pred, axes=1))
    y_true = y_true / mag_true
    y_pred = y_pred / mag_pred
    return 2 * K.T.arccos(K.batch_dot(y_true, y_pred, axes=1)) \
           + K.mean(K.square(mag_true - mag_pred), axis=1)

def angle_loss(y_true, y_pred):
    y_true += 1e-16
    y_pred += 1e-16
    y_true = y_true / K.sqrt(K.batch_dot(y_true, y_true, axes=1))
    y_pred = y_pred / K.sqrt(K.batch_dot(y_pred, y_pred, axes=1))
    return 2 * K.T.arccos(K.batch_dot(y_true, y_pred, axes=1))


def vec_mag_loss(y_true, y_pred):
    y_true += 1e-16
    y_pred += 1e-16
    return K.abs(K.sqrt(K.batch_dot(y_true, y_true, axes=1)) \
                 - K.sqrt(K.batch_dot(y_pred, y_pred, axes=1)))


