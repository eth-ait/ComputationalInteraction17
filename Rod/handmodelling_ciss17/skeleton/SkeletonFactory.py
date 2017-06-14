import SkeletonPolar
import SkeletonXYZ
import SkeletonQuat
import preprocessing.Metadata
import preprocessing.Representations as rep


def create_skeleton_polar_aalto_hand_data(columns):
    return create_skeleton_polar(columns, preprocessing.Metadata.aalto_hand_data)


def create_skeleton_xyz_aalto_hand_data(columns):
    return create_skeleton_xyz(columns, preprocessing.Metadata.aalto_hand_data)


def create_skeleton_quat_aalto_hand_data(columns):
    return create_skeleton_quat(columns, preprocessing.Metadata.aalto_hand_data)


def create_skeleton(columns, metadata, representation):
    if representation == rep.REPRESENTATION_XYZ:
        return create_skeleton_xyz(columns, metadata)
    elif representation == rep.REPRESENTATION_POLAR:
        return create_skeleton_polar(columns, metadata)
    elif representation == rep.REPRESENTATION_QUAT:
        return create_skeleton_quat(columns, metadata)
    else:
        return None



def create_skeleton_polar(columns, metadata):
    # Create the skeleton object:
    skeleton = SkeletonPolar.SkeletonPolar(
        columns=columns,
        features=[metadata.skeleton_node_origin] + metadata.columns_features)

    # Set the name of the origin node:
    skeleton.set_origin_name(metadata.skeleton_node_origin)

    # Create the nodes:
    create_nodes_polar(skeleton, metadata.skeleton_nodes,
                       metadata.node_suffixes_xyz, metadata.node_suffixes_polar)

    # Create the links between the nodes:
    create_links_polar(skeleton, metadata.skeleton_links)

    return skeleton


def create_skeleton_xyz(columns, metadata):
    # Create the skeleton object:
    skeleton = SkeletonXYZ.SkeletonXYZ(
        columns=columns,
        features=[metadata.skeleton_node_origin] + metadata.columns_features)

    # Set the name of the origin node:
    skeleton.set_origin_name(metadata.skeleton_node_origin)

    # Create the links:
    def skeleton_xyz_create_link(label_map, label1, label2, node_suffixes_xyz):
        return [label_map[label1.lower() + node_suffixes_xyz[0].lower()],
                label_map[label2.lower() + node_suffixes_xyz[0].lower()],
                label_map[label1.lower() + node_suffixes_xyz[1].lower()],
                label_map[label2.lower() + node_suffixes_xyz[1].lower()],
                label_map[label1.lower() + node_suffixes_xyz[2].lower()],
                label_map[label2.lower() + node_suffixes_xyz[2].lower()]]

    skeleton.links = []
    for link in metadata.skeleton_links:
        skeleton.links.append(skeleton_xyz_create_link(skeleton.label_map,
                                                       link[0].lower(), link[1].lower(),
                                                       metadata.node_suffixes_xyz))

    return skeleton


def create_nodes_polar(skeleton, nodes, node_suffixes_xyz, node_suffixes_polar):
    skeleton.node_map = {}
    for node in nodes:
        isOrigin = skeleton.origin_name == node.lower()
        if isOrigin:
            v1 = skeleton.label_map[node.lower() + node_suffixes_xyz[0].lower()]
            v2 = skeleton.label_map[node.lower() + node_suffixes_xyz[1].lower()]
            v3 = skeleton.label_map[node.lower() + node_suffixes_xyz[2].lower()]
        else:
            v1 = skeleton.label_map[node.lower() + node_suffixes_polar[0].lower()]
            v2 = skeleton.label_map[node.lower() + node_suffixes_polar[1].lower()]
            v3 = skeleton.label_map[node.lower() + node_suffixes_polar[2].lower()]

        skeleton.node_map[node.lower()] = SkeletonPolar.SkeletonPolar.SkeletonNode(node, v1, v2, v3, isOrigin)


def create_links_polar(skeleton, links):
    for link in links:
        skeleton.node_map[link[0].lower()].add_link(skeleton.node_map[link[1].lower()])


def create_skeleton_quat(columns, metadata):
    return SkeletonQuat.SkeletonQuat(columns,
                                     [metadata.skeleton_node_origin] + metadata.columns_features,
                                     metadata.skeleton_node_origin,
                                     metadata.skeleton_links,
                                     metadata.node_suffixes_xyz,
                                     metadata.node_suffixes_quat)
