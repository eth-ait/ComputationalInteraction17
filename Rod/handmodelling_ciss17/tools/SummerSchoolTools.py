bone_names_map = {}
bone_names_map['origin'] = 'Wrist_Origin'
bone_names_map['wrist_in'] = 'MetroArm_W_In'
bone_names_map['wrist_out'] = 'MetroArm_W_out'
bone_names_map['arm_in'] = 'MetroArm_F_In'
bone_names_map['arm_out'] = 'MetroArm_F_Out'
bone_names_map['centre'] = 'MetroArm_C'
bone_names_map['l1'] = 'MetroArm_L1'
bone_names_map['l2'] = 'MetroArm_L2'
bone_names_map['l3'] = 'MetroArm_L3'
bone_names_map['l4'] = 'MetroArm_L4'
bone_names_map['r1'] = 'MetroArm_R1'
bone_names_map['r2'] = 'MetroArm_R2'
bone_names_map['r3'] = 'MetroArm_R3'
bone_names_map['r4'] = 'MetroArm_R4'
bone_names_map['m1'] = 'MetroArm_M1'
bone_names_map['m2'] = 'MetroArm_M2'
bone_names_map['m3'] = 'MetroArm_M3'
bone_names_map['m4'] = 'MetroArm_M4'
bone_names_map['i1'] = 'MetroArm_I1'
bone_names_map['i2'] = 'MetroArm_I2'
bone_names_map['i3'] = 'MetroArm_I3'
bone_names_map['i4'] = 'MetroArm_I4'
bone_names_map['t1'] = 'MetroArm_T1'
bone_names_map['t2'] = 'MetroArm_T2'
bone_names_map['t3'] = 'MetroArm_T3'
bone_names_map['t4'] = 'MetroArm_T4'


def print_bone_names():
    for b in sorted(bone_names_map.iterkeys()):
        print b


def summer_school_convert_bone_names(names):
    names_converted = []
    for name in names:
        if bone_names_map.has_key(name):
            names_converted.append(bone_names_map[name])
        else:
            names_converted.append(name)
    return names_converted
