def get_xyz_data_for_bone_by_name(data, name, xyz_suffixes):
    colX = name + xyz_suffixes[0]
    colY = name + xyz_suffixes[1]
    colZ = name + xyz_suffixes[2]
    data_vecs = data[[colX, colY, colZ]]
    return data_vecs


class Skeleton(object):

    def __init__(self, columns, features):

        self.origin_name = None
        self.labels = columns
        self.features = features
        self.label_map = self.create_label_map()
        self.node_map = {}


    def set_origin_name(self, origin_name):
        self.origin_name = origin_name.lower()


    def create_label_map(self):
        label_map = {}
        for i in xrange(len(self.labels)):
            key = self.labels[i].lower()
            if not key in label_map:
                label_map[key] = i
        return label_map

    def get_xyz_data_for_bone_by_name(self, data, name, xyz_suffixes):
        colX = name + xyz_suffixes[0]
        colY = name + xyz_suffixes[1]
        colZ = name + xyz_suffixes[2]
        data_vecs = data[[self.label_map[colX.lower()],
                             self.label_map[colY.lower()],
                             self.label_map[colZ.lower()]]]
        return data_vecs