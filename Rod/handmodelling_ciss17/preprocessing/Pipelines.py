import Preprocessing as pre
import Metadata as meta
import pandas as pd
import Representations



def load_aalto_hand_data(filename, header=0, dropna=True, verbose=True):
    data = pd.read_csv(filename,
                       header=header,
                       mangle_dupe_cols=True,
                       usecols=range(0, 86),
                       infer_datetime_format=True,
                       index_col=0)
    if verbose:
        print 'Loaded %d rows with %d columns from file:' % data.shape
        print filename

    if dropna:
        data = pre.drop_missing_values(data, verbose)

    return data


def aalto_remove_hand_center_points(data):
    data_without_center_points = data.drop(
        ['MetroArm_C_In.X', 'MetroArm_C_In.Y','MetroArm_C_In.Z',
         'MetroArm_C_Out.X', 'MetroArm_C_Out.Y', 'MetroArm_C_Out.Z'], axis=1)
    return data_without_center_points


def aalto_remove_e_points(data):
    data_without_center_points = data.drop(
        ['MetroArm_E_In.X', 'MetroArm_E_In.Y','MetroArm_E_In.Z',
         'MetroArm_E_Out.X', 'MetroArm_E_Out.Y', 'MetroArm_E_Out.Z'], axis=1)
    return data_without_center_points

def aalto_merge_hand_center_points(data):
    for suffix in meta.aalto_hand_data.node_suffixes_xyz:
        origin_node_cols = [node + suffix
                            for node in ['MetroArm_C_In', 'MetroArm_C_Out']]
        merged_node_col = 'MetroArm_C' + suffix
        data[merged_node_col] = data[origin_node_cols].mean(axis=1)
    return data



def remove_time_column(data, step_index, verbose):
    data = pre.remove_timestamp_column(data, meta.aalto_hand_data)
    num_features = data.shape[-1]
    if verbose:
        print '%d. Removed the timestamp column ("%s"), leaving %d columns.' \
              % (step_index, meta.aalto_hand_data.column_time, num_features)
    return data


def reorder_feature_columns_to_match_metadata(df, metadata, representation):
    feature_columns = metadata.get_feature_columns_with_suffixes(representation)
    non_feature_columns = [c for c in df.columns.tolist() if c not in feature_columns]
    columns_in_order = non_feature_columns + feature_columns

    return pre.reorder_columns(df, columns_in_order)



def preprocess_aalto_hand_data(data,
                               shift_to_origin=True,
                               remove_timestamp_column=True,
                               representation=Representations.REPRESENTATION_XYZ,
                               reorder_columns=True,
                               verbose=True, returnStepIndex=False):
    step_index = 1

    data = pre.add_origin_column(data, meta.aalto_hand_data.skeleton_node_origin,
                                 meta.aalto_hand_data.skeleton_nodes_for_origin,
                                 meta.aalto_hand_data.node_suffixes_xyz)
    if verbose:
        print '%d. Added an origin column "%s" based on the mean of these columns: %s' \
              % (step_index, meta.aalto_hand_data.skeleton_node_origin,
                 meta.aalto_hand_data.skeleton_nodes_for_origin)
    step_index += 1

    if shift_to_origin:
        data = pre.make_xyz_data_relative_to_origin(data, meta.aalto_hand_data)
        if verbose:
            print '%d. Shifted the x/y/z coordinates so that they are relative to the origin column.' \
                  % step_index
        step_index += 1

    print '%d. Merged the two hand center points.' % step_index
    data = aalto_merge_hand_center_points(data)
    step_index += 1

    print '%d. Removed the original two hand center points.' % step_index
    data = aalto_remove_hand_center_points(data)
    step_index += 1

    print '%d. Removed the extra arm points (E).' % step_index
    data = aalto_remove_e_points(data)
    step_index += 1

    if representation == Representations.REPRESENTATION_POLAR:
        if verbose:
            print '%d. Converted the data from x/y/z coordinates to polar representation ' \
                  '(i.e. two angles and one distance per joint along skeleton graph)' \
                  % step_index
        data = pre.convert_data_xyz_to_polar(data, meta.aalto_hand_data)
        step_index += 1
    elif representation == Representations.REPRESENTATION_QUAT:
        if verbose:
            print '%d. Converted the data from x/y/z coordinates to quaternion representation ' \
                  '(i.e. quaternion and distance per joint along skeleton graph)' \
                  % step_index
        data = pre.convert_data_xyz_to_quat(data, meta.aalto_hand_data)
        step_index += 1

    if reorder_columns:
        data = reorder_feature_columns_to_match_metadata(data,
                                                         meta.aalto_hand_data,
                                                         representation)
        print '%d. Reordered columns: non-feature columns first, ' \
              'then feature columns in order as specified in the metadata (see Metadata.py).' \
                  % step_index
        step_index += 1

    if remove_timestamp_column:
        data = remove_time_column(data, step_index, verbose)
        step_index += 1

    if returnStepIndex:
        return data, step_index
    else:
        return data


def preprocess_aalto_hand_data_sequences(data,
                                         time_per_frame=1 / 240., max_skipped_frames=30,
                                         remove_timestamp_column=True,
                                         min_seq_length=240,
                                         representation=Representations.REPRESENTATION_XYZ,
                                         reorder_columns=True,
                                         verbose=True):
    data, step_index = preprocess_aalto_hand_data(data,
                                                  remove_timestamp_column=False,
                                                  representation=representation,
                                                  reorder_columns=reorder_columns,
                                                  verbose=verbose,
                                                  returnStepIndex=True)

    data = pre.assign_sequence_ids(data, time_per_frame, max_skipped_frames)
    print '%d. Added a sequence id column: Found %d sequences based on %.6fs per frame and a maximum gap of %d skipped frames.' \
          % (step_index, data['Sequence_id'].max(), time_per_frame, max_skipped_frames)
    step_index += 1

    if min_seq_length is not None:
       data = pre.remove_short_sequences(data, min_seq_length)
       data = data.reset_index()
       num_seqs_left = len(data.groupby('Sequence_id'))
       print '%d. Removed %d short sequences (shorter than %d frames), leaving %d sequences.' \
        % (step_index, data['Sequence_id'].max()-num_seqs_left, min_seq_length, num_seqs_left)
       step_index += 1

    if remove_timestamp_column:
        data = remove_time_column(data, step_index, verbose)
        step_index += 1

    return data


def load_leap_hand_data(filename, header=0, dropna=True, verbose=True):
    data = pd.read_csv(filename,
                       header=header,
                       mangle_dupe_cols=True,
                       infer_datetime_format=True,
                       index_col=0)
    if verbose:
        print 'Loaded %d rows with %d columns from file:' % data.shape
        print filename

    if dropna:
        data = pre.drop_missing_values(data, verbose)

    return data


def preprocess_leap_hand_data(data,
                              remove_timestamp_column=True,
                              representation=Representations.REPRESENTATION_XYZ,
                              verbose=True):
    step_index = 1

    data = pre.make_xyz_data_relative_to_origin(data, meta.leap_hand_data)
    if verbose:
        print '%d. Shifted the x/y/z coordinates so that they are relative to the origin column ("%s").' \
              % (step_index, meta.leap_hand_data.skeleton_node_origin)
    step_index += 1

    if representation == Representations.REPRESENTATION_POLAR:
        if verbose:
            print '%d. Converted the data from x/y/z coordinates to polar representation ' \
                  '(i.e. two angles and one distance per joint along skeleton graph)' \
                  % step_index
        data = pre.convert_data_xyz_to_polar(data, meta.leap_hand_data)
        step_index += 1
    elif representation == Representations.REPRESENTATION_QUAT:
        if verbose:
            print '%d. Converted the data from x/y/z coordinates to polar representation ' \
                  '(i.e. quaternion and distance per joint along skeleton graph)' \
                  % step_index
        data = pre.convert_data_xyz_to_quat(data, meta.leap_hand_data)
        step_index += 1

    if remove_timestamp_column:
        data = pre.remove_timestamp_column(data, meta.leap_hand_data)
        num_features = data.shape[-1]
        if verbose:
            print '%d. Removed the timestamp column ("%s"), leaving %d features.' \
                  % (step_index, meta.aalto_hand_data.column_time, num_features)
        step_index += 1

    return data
