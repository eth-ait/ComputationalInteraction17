from sklearn.metrics import mean_squared_error
import preprocessing.Representations as rep
from skeleton.SkeletonQuat import SkeletonQuat
import skeleton.SkeletonFactory as skf
import preprocessing.DataConverterQuat
import pandas as pd
import numpy as np
from keras import backend as K

def convert_xyz_to_quat(data, metadata):
    df = pd.DataFrame(
        index=np.arange(data.shape[0]),
        columns=metadata.get_feature_columns_with_suffixes(rep.REPRESENTATION_XYZ)).fillna(0)
    df[:] = data
    return preprocessing.DataConverterQuat.convert_data_xyz_to_quat(
        df, metadata, is_features_only=True, verbose=False).values


def convert_quat_to_xyz(data, metadata):
    skeleton = skf.create_skeleton(data.columns.tolist(), metadata, rep.REPRESENTATION_QUAT)
    return skeleton.convert_data_quat_to_xyz(data, recreate_bone_graph=True)


def convert(data, metadata, rep1, rep2):
    if rep1 == rep2:
        return data
    if rep2 == rep.REPRESENTATION_XYZ:
        return convert_quat_to_xyz(data, metadata)
    else:
        return convert_xyz_to_quat(data, metadata)


def angle_and_mag_loss(y_true, y_pred, num_bones=25):

    def extract_non_distance_data(data):
        return data[:, get_non_distance_indices(data.shape[1])]

    def get_non_distance_indices(num_cols):
        return [0, 1, 2] + [i for i in range(3, num_cols) if i % 5 != 2]

    def helper_batch_bones_dot(a, b):
        return K.sum(a * b, axis=-1)

    #y_true += 1e-16
    #y_pred += 1e-16

    y_true = extract_non_distance_data(y_true)[:,3:]
    y_pred = extract_non_distance_data(y_pred)[:,3:]

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
    val = K.clip(val, -.9999999, .9999999)
    angle_loss = 2*K.sum(K.T.arccos(val), axis=-1)

    loss = mag_loss + angle_loss
    loss_mse = K.mean(K.square(loss))
    return loss_mse

def compute_mse(model, data, metadata,
                input_representation=rep.REPRESENTATION_XYZ,
                output_representation=rep.REPRESENTATION_XYZ,
                measure_representation=rep.REPRESENTATION_XYZ):

    pred = model.decode(model.encode(data.values))
    pred = convert(pred, metadata, output_representation, measure_representation)

    data_true = convert(data.values, metadata, input_representation, measure_representation)

    mse = mean_squared_error(data_true, pred)
    return mse

def compute_quat_mse(model, data, metadata,
                    input_representation=rep.REPRESENTATION_XYZ,
                    output_representation=rep.REPRESENTATION_XYZ):

    pred = model.decode(model.encode(data.values))
    pred = convert(pred, metadata, output_representation, rep.REPRESENTATION_QUAT)

    data_true = convert(data.values, metadata, input_representation, rep.REPRESENTATION_QUAT)
    quat_loss = angle_and_mag_loss(data_true, pred, num_bones=25)
    return float(quat_loss.eval())