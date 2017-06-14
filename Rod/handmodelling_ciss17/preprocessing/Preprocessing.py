import numpy as np
import DataConverterQuat, DataConverterPolar



def reorder_columns(df, columns_in_order):
    return df[columns_in_order]



def drop_missing_values(data, verbose):
    row_count_before = data.shape[0]
    data = data.dropna()
    row_count_after = data.shape[0]
    if verbose:
        if row_count_before - row_count_after > 0:
            print 'Dropped %d rows due to missing values, leaving %d rows.' \
                % (row_count_before - row_count_after, row_count_after)
        else:
            print 'There are no missing values in this file.'
    return data


def get_mean_of_columns(data, columns):
    return data[columns].mean(axis=1)



def add_origin_column(data, skeleton_node_origin, skeleton_nodes_for_origin, node_suffixes_xyz):

    for suffix in node_suffixes_xyz:
        origin_node_cols = [node + suffix
                            for node in skeleton_nodes_for_origin]
        data[skeleton_node_origin + suffix] = data[origin_node_cols].mean(axis=1)
    return data



def add_origin_column_old(data, metadata):


    normcol_X = metadata.skeleton_nodes_for_origin[0] + metadata.node_suffixes_xyz[0]
    normcol_Y = metadata.skeleton_nodes_for_origin[0] + metadata.node_suffixes_xyz[1]
    normcol_Z = metadata.skeleton_nodes_for_origin[0] + metadata.node_suffixes_xyz[2]
    normcol2_X = metadata.skeleton_nodes_for_origin[1] + metadata.node_suffixes_xyz[0]
    normcol2_Y = metadata.skeleton_nodes_for_origin[1] + metadata.node_suffixes_xyz[1]
    normcol2_Z = metadata.skeleton_nodes_for_origin[1] + metadata.node_suffixes_xyz[2]

    data[metadata.skeleton_node_origin + metadata.node_suffixes_xyz[0]] = \
        (data[normcol_X] + data[normcol2_X]) / 2
    data[metadata.skeleton_node_origin + metadata.node_suffixes_xyz[1]] = \
        (data[normcol_Y] + data[normcol2_Y]) / 2
    data[metadata.skeleton_node_origin + metadata.node_suffixes_xyz[2]] = \
        (data[normcol_Z] + data[normcol2_Z]) / 2

    return data





def convert_data_xyz_to_polar(data, metadata, verbose=True):
    return DataConverterPolar.convert_data_xyz_to_polar(data, metadata, verbose=verbose)


def convert_data_xyz_to_quat(data, metadata, is_features_only=False, verbose=True):
    return DataConverterQuat.convert_data_xyz_to_quat(
        data, metadata, is_features_only=is_features_only, verbose=verbose)

def convert_data_xyz_to_quat_two_hands(data, metadata, is_features_only=False, verbose=True):
    return DataConverterQuat.convert_data_xyz_to_quat_two_hands(
        data, metadata, is_features_only=is_features_only, verbose=verbose)


def make_xyz_data_relative_to_origin(data, metadata):
    return make_xyz_data_relative_to_origin_(data, metadata.skeleton_node_origin,
                                     metadata.node_suffixes_xyz)


def make_xyz_data_relative_to_origin_(data, skeleton_node_origin, node_suffixes_xyz):

    # case where there is just one given existing node to take as the origin
    normcol_X = skeleton_node_origin + node_suffixes_xyz[0]
    normcol_Y = skeleton_node_origin + node_suffixes_xyz[1]
    normcol_Z = skeleton_node_origin + node_suffixes_xyz[2]
    #normcol2_X = normcol_X
    #normcol2_Y = normcol_Y
    #normcol2_Z = normcol_Z

    cols_X = data.filter(regex=("%s.*" % node_suffixes_xyz[0])).columns
    cols_Y = data.filter(regex=("%s.*" % node_suffixes_xyz[1])).columns
    cols_Z = data.filter(regex=("%s.*" % node_suffixes_xyz[2])).columns

    # shift points:
    data_wristnorm = data.copy()
    for col in cols_X:
        data_wristnorm[col] -= (data[normcol_X])
    for col in cols_Y:
        data_wristnorm[col] -= (data[normcol_Y])
    for col in cols_Z:
        data_wristnorm[col] -= (data[normcol_Z])

    return data_wristnorm


def remove_timestamp_column(data, metadata):
    data_without_time = data.drop(metadata.column_time, axis=1)
    return data_without_time







def remove_short_sequences(df, min_seq_len=240):
    df = df.groupby('Sequence_id').filter(lambda x: len(x) > min_seq_len)
    return df


def append_time_diff_column(data):
    data['Time_diff'] = data['Time'].diff()


def remove_time_diff_column(data):
    return data.drop('Time_diff', 1)


def append_sequence_change_marker_column(data, time_diff_tol):
    data['Sequence_change_marker'] = 0
    data.loc[np.abs(data['Time_diff']) > time_diff_tol,
             'Sequence_change_marker'] = 1


def remove_sequence_change_marker_column(data):
    return data.drop('Sequence_change_marker', 1)


def append_sequence_id_column(data):
    data['Sequence_id'] = data['Sequence_change_marker'].cumsum()


def assign_sequence_ids(data, time_per_frame, max_skipped_frames):
    # 1. Add a column that contains the time difference from row to row:
    append_time_diff_column(data)

    # 2. Add a column that marks sequence changes with a "1":
    time_diff_tol = time_per_frame * max_skipped_frames
    append_sequence_change_marker_column(data, time_diff_tol)

    # 3. Add a sequence id column:
    append_sequence_id_column(data)

    # 4. Remove the two helper columns:
    data = remove_time_diff_column(data)
    data = remove_sequence_change_marker_column(data)

    # 5. Move the new sequence id column to be the first column:
    cols = data.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    data = data[cols]

    # 6. Reset the index on this dataframe:
    data = data.reset_index()  # note: this makes "Frame" the first column
    return data

