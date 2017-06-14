import numpy as np
from libraries import transformations as transf
from skeleton.Skeleton import get_xyz_data_for_bone_by_name
from tools.QuaternionTools import qv_mult
import Skeleton

xaxis = np.array([1, 0, 0])


def get_quat_data_for_bone_by_name(data, name, quat_suffixes):
    colW = name + quat_suffixes[0]
    colI = name + quat_suffixes[1]
    colJ = name + quat_suffixes[2]
    colK = name + quat_suffixes[3]
    colD = name + quat_suffixes[4]
    data_vecs = data[[colW, colI, colJ, colK, colD]]
    return data_vecs


class Bone:
    def __init__(self, name='n/a', length=1.0, quat=None):
        self.name = name
        self.length = length
        self.quat = quat

        self.parent = None
        self.children = []

        self.axis = None
        self.pos3D = np.zeros(3)  # used for plotting

    def add_child(self, child):
        self.children.append(child)
        child.parent = self


class SkeletonQuat(Skeleton.Skeleton):
    def __init__(self, columns, features,
                 node_origin, links,
                 node_suffixes_xyz, node_suffixes_quat):
        Skeleton.Skeleton.__init__(self, columns, features)
        self.pos3D = np.zeros(3)
        self.bone_map = {}
        self.root = None
        # self.metadata = metadata
        self.node_origin = node_origin
        self.links = links
        self.node_suffixes_xyz = node_suffixes_xyz
        self.node_suffixes_quat = node_suffixes_quat
        self.setup_bone_graph()

    def add_bone(self, name):
        bone = Bone(name=name, length=0, quat=None)
        self.bone_map[name] = bone
        return bone

    def get_quat_data_for_bone_by_name(self, data, name, quat_suffixes):
        colW = name + quat_suffixes[0]
        colI = name + quat_suffixes[1]
        colJ = name + quat_suffixes[2]
        colK = name + quat_suffixes[3]
        colD = name + quat_suffixes[4]
        data_vecs = data[[self.label_map[colW.lower()],
                          self.label_map[colI.lower()],
                          self.label_map[colJ.lower()],
                          self.label_map[colK.lower()],
                          self.label_map[colD.lower()]]]
        return data_vecs

    def create_bone_graph(self, links):

        for link in links:

            # create the bones if they do not already exist:
            for i in xrange(2):
                bone_name = link[i]
                if not self.bone_map.has_key(bone_name):
                    self.add_bone(name=bone_name)

            # link the bones as parent-child:
            bone = self.bone_map[link[0]]
            bone2 = self.bone_map[link[1]]
            bone.add_child(bone2)

    def setup_bone_graph(self):
        self.bone_map = {}
        self.root = self.add_bone(self.node_origin)
        self.create_bone_graph(self.links)

    def set_data(self, data_row, recreate_bone_graph=True):

        # set origin position:
        self.pos3D = self.get_xyz_data_for_bone_by_name(data_row,
                                                        self.node_origin,
                                                        self.node_suffixes_xyz)

        # set up the bone graph if necessary:
        if recreate_bone_graph:
            self.setup_bone_graph()

        # set the bone quat data:
        for bone in self.bone_map.itervalues():
            if bone.name == self.node_origin:  # TEST EXTRA QUAT BONE:
                continue
            data_quat = self.get_quat_data_for_bone_by_name(data_row,
                                                            bone.name,
                                                            self.node_suffixes_quat)
            #print bone.name, data_quat
            if bone.name == self.node_origin:
                data_quat[4] = 1
            bone.quat = data_quat[0:4]#transf.unit_vector(data_quat[0:4])# unit...
            bone.length = data_quat[4]

        # update the layout (i.e. the 3D positions) for plotting
        self.layout(self.root)

    def layout_offset(self, root, offset):
        root.pos3D += offset
        for child in root.children:
            self.layout_offset(child, offset)

    def layout(self, root):
        if root.parent is None:
            # 04.04.2017 Daniel: set root of skeleton to zero location, then shift everything in the end
            # this way, we properly separate 3d location of the whole hand from the relative locations
            root.pos3D = np.array([0., 0., 0.])  # self.pos3D
            root.axis = transf.unit_vector(root.pos3D - xaxis)
        else:
            root.pos3D = root.parent.pos3D + root.length * qv_mult(root.quat, root.parent.axis)
            root.axis = transf.unit_vector(root.pos3D - root.parent.pos3D)

        for child in root.children:
            self.layout(child)

        if root.parent is None:
            self.layout_offset(root, self.pos3D)

    def plot_rec(self, ax, root, showJoints, c, cmap, lw, alpha, show_bone_names=False):
        if show_bone_names:
            ax.text(root.pos3D[0], root.pos3D[1], root.pos3D[2], root.name)
        if showJoints:
            ax.scatter(root.pos3D[0], root.pos3D[1], root.pos3D[2], c=c, lw=lw, alpha=alpha)
        for child in root.children:
            ax.plot([root.pos3D[0], child.pos3D[0]],
                    [root.pos3D[1], child.pos3D[1]],
                    [root.pos3D[2], child.pos3D[2]],
                    c=c, lw=lw, alpha=alpha)
            self.plot_rec(ax, child, showJoints, c, cmap, lw, alpha, show_bone_names=show_bone_names)

    def plot(self, ax, data, showJoints=False, c='k', cmap=None, lw=1, alpha=1):
        rows, cols = data.shape
        for row in xrange(rows):
            cs = None
            if cmap != None:
                cs = [cmap(v)[0:3] for v in np.linspace(0, 1, rows)]
            self.set_data(data[row, :], recreate_bone_graph=row == 0)
            self.plot_rec(ax, self.root, showJoints, c, cs, lw, alpha)

    def plot2D_rec(self, ax, root, showJoints, c, lw, alpha,
                   show_bone_names=False, scale=1, offset=[0, 0]):
        if show_bone_names:
            ax.text(root.pos3D[0] * scale + offset[0], root.pos3D[1] * scale + offset[1], root.name)
        if showJoints:
            ax.scatter(root.pos3D[0] * scale + offset[0], root.pos3D[1] * scale + offset[1],
                       c=c, lw=lw, alpha=alpha)
        for child in root.children:
            ax.plot([root.pos3D[0] * scale + offset[0], child.pos3D[0] * scale + offset[0]],
                    [root.pos3D[1] * scale + offset[1], child.pos3D[1] * scale + offset[1]],
                    c=c, lw=lw, alpha=alpha)
            self.plot2D_rec(ax, child, showJoints, c, lw, alpha,
                            show_bone_names=show_bone_names, scale=scale, offset=offset)

    def plot2D(self, ax, data, showJoints=False, c='k', lw=1,
               alpha=1, scale=1, offsets=None):
        rows, cols = data.shape
        for row in xrange(rows):
            if not isinstance(c, basestring):
                c_here = c[row]
            else:
                c_here = c

            self.set_data(data[row, :], recreate_bone_graph=row == 0)
            offset_row = [0, 0] if offsets is None else offsets[row, :]
            self.plot2D_rec(ax, self.root, showJoints, c_here, lw, alpha,
                            scale=scale, offset=offset_row)

    def convert_data_quat_to_xyz(self, data, recreate_bone_graph=False):
        rows, cols = data.shape

        data_xyz = np.zeros((rows, len(self.bone_map) * 3))
        for row in xrange(rows):

            self.set_data(data[row, :], recreate_bone_graph=(recreate_bone_graph and row == 0))
            col_i = 0
            for bone_name in self.features:
                bone = self.bone_map[bone_name]
                # print bone_name,  bone.pos3D
                data_xyz[row, col_i:col_i + 3] = bone.pos3D
                col_i += 3

        return data_xyz
