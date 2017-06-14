import numpy as np

import Skeleton


class SkeletonXYZ(Skeleton.Skeleton):


    def __init__(self, columns, features):
        Skeleton.Skeleton.__init__(self, columns, features)
        self.links = []


    def plot(self, ax, data, showJoints=False, c='k', cmap=None, lw=1, alpha=1):

        rows, cols = data.shape

        cs = None
        if cmap != None:
            cs = [cmap(v)[0:3] for v in np.linspace(0, 1, rows)]

        for row in xrange(rows):
            if cs != None:
                c = cs[row]
            for link in self.links:
                x1 = data[row, link[0]]
                y1 = data[row, link[2]]
                z1 = data[row, link[4]]
                x2 = data[row, link[1]]
                y2 = data[row, link[3]]
                z2 = data[row, link[5]]
                ax.plot([x1, x2], [y1, y2], [z1, z2], c=c, lw=lw, alpha=alpha)
        if showJoints:
            ax.scatter(data[:,0::3], data[:,1::3], data[:,2::3], c=c, lw=lw, alpha=alpha)