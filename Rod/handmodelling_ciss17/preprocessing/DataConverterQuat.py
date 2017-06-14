from libraries import transformations as transf
from skeleton.Skeleton import get_xyz_data_for_bone_by_name
import numpy as np
import pandas as pd
import Preprocessing as pre


class TmpBone:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self


def get_axis3D_df(n_rows, dim):
    axis_df = np.zeros((n_rows, 3))
    axis_df[:,dim] = 1
    return axis_df

def quat_from_vecs_df(data_vecs, data_vecs2):
    q = -1*np.cross(data_vecs, data_vecs2)
    q2 = np.linalg.norm(data_vecs, axis=1) * np.linalg.norm(data_vecs2, axis=1) \
        + np.einsum('ij,ij->i', data_vecs, data_vecs2)
    q = np.hstack((q2.reshape(-1,1),q))
    q = transf.unit_vector(q, axis=1)
    return q

def quat_between_bones_df(bone, data, node_suffixes_xyz):

    # get columns with x, y, z values for this bone:
    data_xyz = get_xyz_data_for_bone_by_name(data, bone.name, node_suffixes_xyz)

    # if it is the root bone (i.e. has no parent), we take the rotation to the x-axis:
    # this should never be reached given the way we call this method
    if bone.parent is None:
        # print 'is root: ' + bone.name
        xaxis_df = 1*get_axis3D_df(n_rows=data_xyz.shape[0], dim=0)
        q = quat_from_vecs_df(data_xyz, xaxis_df)# TEST EXTRA QUAT BONE: xaxis_df, xaxis_df
        return q

    # else this bone has a parent:
    else:
        # get the columns with x, y, z values for this bone's parent:
        data_xyz_parent = get_xyz_data_for_bone_by_name(
            data, bone.parent.name, node_suffixes_xyz)

        if bone.parent.parent is None:
            # print 'is first level bone: ' + bone.name
            xaxis_df = 1*get_axis3D_df(n_rows=data_xyz.shape[0], dim=0)
            q = quat_from_vecs_df(data_xyz.values - data_xyz_parent.values,
                                  data_xyz_parent.values - xaxis_df)
            return q
        else:
            # print 'is > level 1 bone: ' + bone.name
            data_xyz_grandparent = get_xyz_data_for_bone_by_name(
                data, bone.parent.parent.name, node_suffixes_xyz)
            q = quat_from_vecs_df(data_xyz.values - data_xyz_parent.values,
                                  data_xyz_parent.values - data_xyz_grandparent.values)
            return q

    colX2 = bone.parent.name + metadata.node_suffixes_xyz[0]
    colY2 = bone.parent.name + metadata.node_suffixes_xyz[1]
    colZ2 = bone.parent.name + metadata.node_suffixes_xyz[2]
    data_vecs2 = data[[colX2, colY2, colZ2]]

    q = quat_from_vecs_df(data_vecs, data_vecs2)
    return q


def convert_data_xyz_to_quat(data, metadata, is_features_only=False, verbose=True):
    return convert_data_xyz_to_quat_helper(
        data,
        [metadata.column_time] if not is_features_only else None,
        metadata.skeleton_node_origin,
        metadata.node_suffixes_xyz,
        metadata.node_suffixes_quat,
        metadata.skeleton_links,
        verbose=verbose)


def convert_data_xyz_to_quat_two_hands(data, metadata2, is_features_only=False, verbose=True):
    data_left = convert_data_xyz_to_quat_helper(
        data,
        metadata2.columns_non_mocap if not is_features_only else None,
        metadata2.skeleton_node_origin_left,
        metadata2.node_suffixes_xyz,
        metadata2.node_suffixes_quat,
        metadata2.skeleton_links_left,
        verbose=verbose)

    data_right = convert_data_xyz_to_quat_helper(
        data,
        metadata2.columns_non_mocap if not is_features_only else None,
        metadata2.skeleton_node_origin_right,
        metadata2.node_suffixes_xyz,
        metadata2.node_suffixes_quat,
        metadata2.skeleton_links_right,
        verbose=verbose)

    if not is_features_only:
        data_both = data_left.merge(data_right, how='outer')
    else:
        data_both = pd.concat((data_left, data_right), axis=1)  #
    return data_both

def convert_data_xyz_to_quat_helper(data,
                                    columns_non_features,
                                    skeleton_node_origin,
                                    node_suffixes_xyz,
                                    node_suffixes_quat,
                                    skeleton_links,
                                    verbose=True):

    origin_columns = [skeleton_node_origin + node_suffixes_xyz[0],
               skeleton_node_origin + node_suffixes_xyz[1],
               skeleton_node_origin + node_suffixes_xyz[2]]

    features_to_copy = None
    if columns_non_features is not None:
        features_to_copy = columns_non_features + origin_columns
    else:
        features_to_copy = origin_columns

    df = data[features_to_copy].copy()

    #origin_data = data[origin_columns]

    data_shifted = pre.make_xyz_data_relative_to_origin_(
        data, skeleton_node_origin, node_suffixes_xyz)

    #print data_shifted['Hands_L_Win_x'].head()

    #TEST EXTRA QUAT BONE:
    #data[skeleton_node_origin + '_bone' + node_suffixes_xyz[0]] = \
    #    data[skeleton_node_origin + node_suffixes_xyz[0]]+1
    #data[skeleton_node_origin + '_bone' + node_suffixes_xyz[1]] = \
    #    data[skeleton_node_origin + node_suffixes_xyz[1]]
    #data[skeleton_node_origin + '_bone' + node_suffixes_xyz[2]] = \
    #    data[skeleton_node_origin + node_suffixes_xyz[2]]


    # extract graph structure
    bone_map = {}
    for link in skeleton_links:

        # create bones if they do not already exist:
        for i in xrange(2):
            if not bone_map.has_key(link[i]):
                bone_map[link[i]] = TmpBone(link[i])

        bone = bone_map[link[0]]
        bone2 = bone_map[link[1]]
        bone.add_child(bone2)

    # create columns

    # create columns for each bone:
    for bone in bone_map.itervalues():

        # create quat columns:
        if bone.name == skeleton_node_origin:
            # print 'skipped, no need for quats for root node'
            continue
        q = quat_between_bones_df(bone, data_shifted, node_suffixes_xyz)

        #if 'Win' in bone.name:
        #    print bone.name, q[0:5,:]

        # TEST EXTRA QUAT BONE:
        #if bone.name == skeleton_node_origin+'_bone':
        #    q = transf.quaternion_about_axis(np.deg2rad(0), [0, 1, 0])
        #    q = np.array([q for i in xrange(data.shape[0])])
        #    print q

        for i in xrange(4):
            col_new_quat = bone.name + node_suffixes_quat[i]
            df[col_new_quat] = q[:, i]
        col_new_length = bone.name + node_suffixes_quat[4]

        # create length column:
        if bone.parent is not None:
            data_xyz = get_xyz_data_for_bone_by_name(data_shifted, bone.name, node_suffixes_xyz)
            data_xyz2 = get_xyz_data_for_bone_by_name(data_shifted, bone.parent.name, node_suffixes_xyz)
            df[col_new_length] = np.linalg.norm(data_xyz2.values - data_xyz.values, axis=1)
        #else:
        #    df[col_new_length] = 1 # TEST EXTRA QUAT BONE:
    # create length columns:
    #for link in metadata.skeleton_links:
    #    data_xyz = get_xyz_data_for_bone_by_name(data, link[0], metadata.node_suffixes_xyz)
    #    data_xyz2 = get_xyz_data_for_bone_by_name(data, link[1], metadata.node_suffixes_xyz)
    #    col_new_length = link[1] + metadata.node_suffixes_quat[4]
    #    df[col_new_length] = np.linalg.norm(data_xyz2.values - data_xyz.values, axis=1)

    return df
