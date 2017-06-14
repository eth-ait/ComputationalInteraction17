import numpy as np


def convert_data_xyz_to_polar(data, metadata, verbose=True):

    df = data[[metadata.column_time,
               metadata.skeleton_node_origin + metadata.node_suffixes_xyz[0],
               metadata.skeleton_node_origin + metadata.node_suffixes_xyz[1],
               metadata.skeleton_node_origin + metadata.node_suffixes_xyz[2]]].copy()

    for link in metadata.skeleton_links:
        colX = link[0] + metadata.node_suffixes_xyz[0]
        colY = link[0] + metadata.node_suffixes_xyz[1]
        colZ = link[0] + metadata.node_suffixes_xyz[2]

        colX2 = link[1] + metadata.node_suffixes_xyz[0]
        colY2 = link[1] + metadata.node_suffixes_xyz[1]
        colZ2 = link[1] + metadata.node_suffixes_xyz[2]

        col_new_a = link[1] + metadata.node_suffixes_polar[0]
        col_new_b = link[1] + metadata.node_suffixes_polar[1]
        col_new_d = link[1] + metadata.node_suffixes_polar[2]

        df[col_new_a] = np.arctan2(data[colY2] - data[colY], data[colX2] - data[colX])
        df[col_new_b] = np.pi / 2 - np.arctan((data[colZ2] - data[colZ]) /
                                              np.linalg.norm([data[colX2].values - data[colX].values,
                                                              data[colY2].values - data[colY].values]))
        df[col_new_d] = np.sqrt((data[colZ2] - data[colZ])**2
                                + (data[colY2] - data[colY])**2
                                + (data[colX2] - data[colX])**2)

    return df