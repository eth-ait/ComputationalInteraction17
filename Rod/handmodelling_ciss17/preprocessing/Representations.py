REPRESENTATION_XYZ = 0
REPRESENTATION_POLAR = 1
REPRESENTATION_QUAT = 2


def get_suffixes(metadata, representation):
    if representation==REPRESENTATION_XYZ:
        return metadata.node_suffixes_xyz
    elif representation==REPRESENTATION_POLAR:
        return metadata.node_suffixes_polar
    elif representation==REPRESENTATION_QUAT:
        return metadata.node_suffixes_quat
    else:
        return None