import numpy as np

import Skeleton


class SkeletonPolar(Skeleton.Skeleton):


    class SkeletonNode:
        def __init__(self, label, v1, v2, v3, isOrigin):
            self.v1 = v1
            self.v2 = v2
            self.v3 = v3
            self.label = label
            self.isOrigin = isOrigin
            self.links = []

        def add_link(self, node):
            self.links.append(node)

        def set_coordinates(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    def __init__(self, columns, features):
        Skeleton.Skeleton.__init__(self, columns, features)
        self.links = None


    def traverse_set_coordinates(self, root, data_row):
        for node in root.links:
            node.x = root.x + data_row[node.v3] * np.cos(data_row[node.v1]) * np.sin(data_row[node.v2])
            node.y = root.y + data_row[node.v3] * np.sin(data_row[node.v1]) * np.sin(data_row[node.v2])
            node.z = root.z + data_row[node.v3] * np.cos(data_row[node.v2])
            self.traverse_set_coordinates(node, data_row)


    def get_xyz_coordinates(self, data):

        coords = []
        rows, cols = data.shape
        root = self.node_map[self.origin_name]
        for row in xrange(rows):
            root.x = data.values[row, root.v1]
            root.y = data.values[row, root.v2]
            root.z = data.values[row, root.v3]
            self.traverse_set_coordinates(root, data.values[row, :])
            coords_row = []
            for label in self.labels:
                coords_row.append(data.values[row, self.label_map[label.lower()]])
            coords.append(coords_row)
        return np.array(coords)


    def plot(self, ax, data, showJoints=False, c='k', cmap=None, lw=1, alpha=0.25):

        rows, cols = data.shape
        root = self.node_map[self.origin_name]

        cs = None
        if cmap != None:
            cs = [cmap(v)[0:3] for v in np.linspace(0, 1, rows)]

        for row in xrange(rows):
            if cs != None:
                c = cs[row]
            root.x = data.values[row, root.v1]
            root.y = data.values[row, root.v2]
            root.z = data.values[row, root.v3]
            self.traverse_set_coordinates(root, data.values[row, :])
            #ax.scatter([root.x], [root.y], [root.z], c='r', s=128)
            for node in self.node_map.itervalues():
                for node2 in node.links:
                    ax.plot([node.x, node2.x], [node.y, node2.y], [node.z, node2.z], c=c, lw=lw, alpha=alpha)
                if showJoints:
                    ax.scatter([node.x], [node.y], [node.z], c=c, lw=lw, alpha=alpha)