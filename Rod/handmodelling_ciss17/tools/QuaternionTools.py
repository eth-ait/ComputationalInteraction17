from libraries import transformations as transf
import numpy as np


# rotate vector v1 by quaternion q1
def qv_mult(q1, v1, verbose=False):
    v1 = transf.unit_vector(v1)
    q2 = [0] + list(v1)

    if verbose:
        print 'extended axis=%s' % q2
        print 'mult1=%s' % transf.quaternion_multiply(q1, q2)
        print 'conj=%s' % transf.quaternion_conjugate(q1)
        print 'mult2=%s' % transf.quaternion_multiply(
        transf.quaternion_multiply(q1, q2),
        transf.quaternion_conjugate(q1)
    )[1:4]
    return transf.quaternion_multiply(
        transf.quaternion_multiply(q1, q2),
        transf.quaternion_conjugate(q1)
    )[1:4]


def quat_from_vecs(v1, v2):
    q = list(-1*np.cross(v1, v2))
    q = [transf.vector_norm(v1) * transf.vector_norm(v2) + np.dot(v1, v2)] + q
    q = transf.unit_vector(q)
    return q

# dataframe version:
def quat_from_vecs_df(data_vecs, data_vecs2):
    q = -1*np.cross(data_vecs, data_vecs2)
    q2 = np.linalg.norm(data_vecs, axis=1) * np.linalg.norm(data_vecs2, axis=1) \
        + np.einsum('ij,ij->i', data_vecs, data_vecs2)
    q = np.hstack((q2.reshape(-1,1),q))
    q = transf.unit_vector(q, axis=1)
    return q
