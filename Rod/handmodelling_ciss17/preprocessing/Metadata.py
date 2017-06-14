import preprocessing.Representations as rep


class DatasetMetadata:
    def __init__(self, node_suffixes_xyz, node_suffixes_polar, node_suffixes_quat,
                 skeleton_nodes, skeleton_links,
                 skeleton_nodes_for_origin, skeleton_node_origin,
                 column_time, columns_non_mocap, columns_features, hand='NA'):
        self.node_suffixes_xyz = node_suffixes_xyz
        self.node_suffixes_polar = node_suffixes_polar
        self.node_suffixes_quat = node_suffixes_quat
        self.skeleton_nodes = skeleton_nodes
        self.skeleton_links = skeleton_links
        self.skeleton_nodes_for_origin = skeleton_nodes_for_origin
        self.skeleton_node_origin = skeleton_node_origin
        self.column_time = column_time
        self.columns_non_mocap = columns_non_mocap
        self.columns_features = columns_features
        self.hand = hand

    def get_feature_columns_with_suffixes(self, representation):
        suffixes = rep.get_suffixes(self, representation)
        feature_columns = \
            [feature + suffix for feature in self.columns_features \
             for suffix in suffixes]

        feature_columns = \
            [self.skeleton_node_origin + suffix \
             for suffix in self.node_suffixes_xyz] \
            + feature_columns
        return feature_columns

    def get_xyz_feature_column_index(self, feature):

        cols = self.get_feature_columns_with_suffixes(representation=rep.REPRESENTATION_XYZ)
        for i in xrange(len(cols)):
            if cols[i] == feature:
                return i
        return None

    def get_feature_column_indices(self, features, representation, features_have_suffixes=False):

        indices = []
        cols = self.get_feature_columns_with_suffixes(representation=representation)
        for feature in features:
            for i in xrange(len(cols)):
                if (not features_have_suffixes and feature in cols[i])\
                or (features_have_suffixes and feature == cols[i]):
                    indices.append([i])

        return indices

    def index_of_bone(self, bone, bone_list):
        for i in xrange(len(bone_list)):
            if bone == bone_list[i]:
                return i
        return -1

# ===============================================================
# Metadata for the aalto hand dataset:
aalto_hand_data_column_time = 'Time'
aalto_hand_data_columns_non_mocap = ['Time']
aalto_hand_data_skeleton_nodes_for_origin = ['MetroArm_W_In', 'MetroArm_W_out']
aalto_hand_data_skeleton_node_origin = 'Wrist_Origin'

aalto_hand_data_skeleton_node_suffixes_xyz = ['.X', '.Y', '.Z']
aalto_hand_data_skeleton_node_suffixes_polar = ['.a', '.b', '.d']
aalto_hand_data_skeleton_node_suffixes_quat = ['.w', '.i', '.j', '.k', '.d']
aalto_hand_data_columns_features = [
    'MetroArm_W_In', 'MetroArm_W_out',
    #'MetroArm_E_In', 'MetroArm_E_Out',
    'MetroArm_F_In', 'MetroArm_F_Out',
    #'MetroArm_C_In', 'MetroArm_C_Out',
    'MetroArm_C',
    'MetroArm_L1', 'MetroArm_L2', 'MetroArm_L3', 'MetroArm_L4',
    'MetroArm_R1', 'MetroArm_R2', 'MetroArm_R3', 'MetroArm_R4',
    'MetroArm_M1', 'MetroArm_M2', 'MetroArm_M3', 'MetroArm_M4',
    'MetroArm_I1', 'MetroArm_I2', 'MetroArm_I3', 'MetroArm_I4',
    'MetroArm_T1', 'MetroArm_T2', 'MetroArm_T3', 'MetroArm_T4']
aalto_hand_data_skeleton_nodes = [aalto_hand_data_skeleton_node_origin] \
                                 + aalto_hand_data_columns_features




aalto_hand_data_skeleton_links = [
    ['Wrist_Origin', 'MetroArm_W_In'],
    ['MetroArm_W_In', 'MetroArm_F_In'],
    #['MetroArm_F_In', 'MetroArm_E_In'],

    ['Wrist_Origin', 'MetroArm_W_out'],
    ['MetroArm_W_out', 'MetroArm_F_Out'],
    #['MetroArm_F_Out', 'MetroArm_E_Out'],

    #['Wrist_Origin', 'MetroArm_C_In'], ['Wrist_Origin', 'MetroArm_C_Out'],
    ['Wrist_Origin', 'MetroArm_C'],

    ['MetroArm_C', 'MetroArm_L1'], ['MetroArm_L1', 'MetroArm_L2'],
    ['MetroArm_L2', 'MetroArm_L3'], ['MetroArm_L3', 'MetroArm_L4'],

    ['MetroArm_C', 'MetroArm_R1'], ['MetroArm_R1', 'MetroArm_R2'],
    ['MetroArm_R2', 'MetroArm_R3'], ['MetroArm_R3', 'MetroArm_R4'],

    ['MetroArm_C', 'MetroArm_M1'], ['MetroArm_M1', 'MetroArm_M2'],
    ['MetroArm_M2', 'MetroArm_M3'], ['MetroArm_M3', 'MetroArm_M4'],

    ['MetroArm_C', 'MetroArm_I1'], ['MetroArm_I1', 'MetroArm_I2'],
    ['MetroArm_I2', 'MetroArm_I3'], ['MetroArm_I3', 'MetroArm_I4'],

    ['MetroArm_C', 'MetroArm_T1'], ['MetroArm_T1', 'MetroArm_T2'],
    ['MetroArm_T2', 'MetroArm_T3'], ['MetroArm_T3', 'MetroArm_T4']]



aalto_hand_data = DatasetMetadata(aalto_hand_data_skeleton_node_suffixes_xyz,
                                  aalto_hand_data_skeleton_node_suffixes_polar,
                                  aalto_hand_data_skeleton_node_suffixes_quat,
                                  aalto_hand_data_skeleton_nodes,
                                  aalto_hand_data_skeleton_links,
                                  aalto_hand_data_skeleton_nodes_for_origin,
                                  aalto_hand_data_skeleton_node_origin,
                                  aalto_hand_data_column_time,
                                  aalto_hand_data_columns_non_mocap,
                                  aalto_hand_data_columns_features)






# ===============================================================




# ===============================================================
# Metadata for leap motion hand data:
leap_hand_data_column_time = 'Time'
leap_hand_data_skeleton_nodes_for_origin = None
leap_hand_data_skeleton_node_origin = 'Wrist'
leap_hand_data_columns_non_mocap = ['Time']

leap_hand_data_skeleton_node_suffixes_xyz = ['.X', '.Y', '.Z']
leap_hand_data_skeleton_node_suffixes_polar = ['.a', '.b', '.d']
leap_hand_data_skeleton_node_suffixes_quat = ['.w', '.i', '.j', '.k', '.d']
leap_hand_data_columns_features = [
    'Wrist',
    'Thumb_1', 'Thumb_1', 'Thumb_3', 'Thumb_4',
    'Index_1', 'Index_2', 'Index_3','Index_4',
    'Middle_1', 'Middle_2', 'Middle_3', 'Middle_4',
    'Ring_1', 'Ring_2', 'Ring_3', 'Ring_4',
    'Little_1', 'Little_2', 'Little_3', 'Little_4']
leap_hand_data_skeleton_nodes = [leap_hand_data_skeleton_node_origin] \
                                 + leap_hand_data_columns_features
leap_hand_data_skeleton_links = [
    ['Wrist', 'Thumb_1'], ['Thumb_1', 'Thumb_2'],
    ['Thumb_2', 'Thumb_3'], ['Thumb_3', 'Thumb_4'],

    ['Wrist', 'Index_1'], ['Index_1', 'Index_2'],
    ['Index_2', 'Index_3'], ['Index_3', 'Index_4'],

    ['Wrist', 'Middle_1'], ['Middle_1', 'Middle_2'],
    ['Middle_2', 'Middle_3'], ['Middle_3', 'Middle_4'],

    ['Wrist', 'Ring_1'], ['Ring_1', 'Ring_2'],
    ['Ring_2', 'Ring_3'], ['Ring_3', 'Ring_4'],

    ['Wrist', 'Little_1'], ['Little_1', 'Little_2'],
    ['Little_2', 'Little_3'], ['Little_3', 'Little_4']]

leap_hand_data = DatasetMetadata(leap_hand_data_skeleton_node_suffixes_xyz,
                                 leap_hand_data_skeleton_node_suffixes_polar,
                                 leap_hand_data_skeleton_node_suffixes_quat,
                                 leap_hand_data_skeleton_nodes,
                                 leap_hand_data_skeleton_links,
                                 leap_hand_data_skeleton_nodes_for_origin,
                                 leap_hand_data_skeleton_node_origin,
                                 leap_hand_data_column_time,
                                 leap_hand_data_columns_non_mocap,
                                 leap_hand_data_columns_features)
# ===============================================================
