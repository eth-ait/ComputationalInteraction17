import ipywidgets as widgets
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import seaborn as sns
from ipywidgets import interact
import preprocessing.Representations as rep
from skeleton.SkeletonQuat import SkeletonQuat

from tools.SummerSchoolTools import summer_school_convert_bone_names

import skeleton.SkeletonFactory as skf


def plot_hand_data_latent_space_ND(data, model_encoder, title=None, **kwargs):
    data_encoded = model_encoder.encode(data)
    data_encoded_df = pd.DataFrame(data_encoded) # wrap as dataframe for seaborn
    #sns.pairplot(data_encoded_df, plot_kws=dict(alpha=0.01, lw=0, s=20))
    g = sns.pairplot(data_encoded_df, plot_kws=dict(kwargs))
    g.fig.suptitle(title)


def int_plot_interpolate_latent_space(model, data, metadata,
                                      frame1, frame2, steps, representation=rep.REPRESENTATION_XYZ, **kwargs):
    n_dim = model.latent_dim
    skeleton = skf.create_skeleton(data.columns.tolist(), metadata, representation)

    frame1_encoded = model.encode(data.values[[frame1]])[0]
    frame2_encoded = model.encode(data.values[[frame2]])[0]

    # interpolate between the frames in latent space:
    data_interp = np.repeat(np.linspace(0, 1, steps), n_dim).reshape(-1, n_dim)
    for d in xrange(n_dim):
        data_interp[:, d] = [(1 - a) * frame1_encoded[d] + a * frame2_encoded[d] for a in data_interp[:, d]]

    # reconstruct the hand points based on the interpolated latent values:
    data_interp_reconstructed = model.decode(data_interp)

    # plot the reconstruction:
    def int_plot_f(step, elev, azim):
        fig = plt.figure(figsize=(8, 8))
        if kwargs.has_key('title'):
            plt.title(kwargs['title'])

        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=elev, azim=azim)

        if skeleton != None:
            cmap = cm.winter
            skeleton.plot(ax, data.values[[frame1]], c=cmap(0), cmap=None, lw=2, alpha=0.75)
            skeleton.plot(ax, data.values[[frame2]], c=cmap(1.0), cmap=None, lw=2, alpha=0.75)
            skeleton.plot(ax, data_interp_reconstructed[[step]], c=cmap(step*1.0/steps),
                          lw=4, alpha=0.75)
        plt.tight_layout()
        plt.show()

    interact(int_plot_f,
             step=widgets.IntSlider(min=0, max=steps - 1, step=1, value=steps / 2),
             elev=widgets.IntSlider(min=-90, max=90, step=1, value=45),
             azim=widgets.IntSlider(min=0, max=360, step=1, value=320))



def int_plot_latent_dimensions(model, data, metadata,
                               steps, frame, representation=rep.REPRESENTATION_XYZ, **kwargs):
    data_encoded = model.encode(data.values)
    data_encoded_modified = np.repeat(data_encoded[[frame]], steps, axis=0)

    n_dim = model.latent_dim
    skeleton = skf.create_skeleton(data.columns.tolist(), metadata, representation)

    data_reconstructed = []

    for dim in xrange(n_dim):
        data_encoded_modified[:, dim] = np.linspace(
            min(data_encoded[:, dim]),
            max(data_encoded[:, dim]), steps)
        # print 'min value:', min(data_encoded[:,dim]), ', max value:', max(data_encoded[:,dim])
        data_reconstructed.append(model.decode(data_encoded_modified))

    fig_rows = int(np.floor(np.sqrt(n_dim+1)))
    fig_cols = int(np.ceil(np.sqrt(n_dim)))

    def int_plot_f(i):
        fig = plt.figure(figsize=(fig_cols * 5, fig_rows * 5))
        if kwargs.has_key('title'):
            plt.title(kwargs['title'])

        gs1 = gridspec.GridSpec(fig_rows, fig_cols)
        for dim in xrange(n_dim):
            ax = fig.add_subplot(gs1[dim], projection='3d')  # , adjustable='box', aspect=1)
            ax.set_xlim(-0.2, 0.2)
            ax.set_ylim(-0.2, 0.2)
            ax.set_zlim(-0.2, 0.2)
            skeleton.plot(ax, data_reconstructed[dim][[i]], c='k', alpha=0.75)
            ax.scatter([0], [0], [0], c='k', marker='o')
            plt.title('Latent Dimension #' + str(dim))
        plt.show()

    interact(int_plot_f, i=(0, steps - 1))




def plot_latent_dimensions(model, data, metadata, steps, frame,
                           plot_static=True, plot_dynamics=False, verbose=False,
                           representation=rep.REPRESENTATION_XYZ, **kwargs):
    data_encoded = model.encode(data.values)
    data_encoded_modified = np.repeat(data_encoded[[frame]], steps, axis=0)

    n_dim = model.latent_dim
    skeleton = skf.create_skeleton(data.columns.tolist(), metadata, representation)

    fig_rows = int(np.floor(np.sqrt(n_dim+1)))
    fig_cols = int(np.ceil(np.sqrt(n_dim)))


    if verbose:
        print 'figure layout:', fig_rows, fig_cols

    fig = plt.figure(figsize=(fig_cols * 5, fig_rows * 5))
    if kwargs.has_key('title'):
        plt.title(kwargs['title'])
    gs1 = gridspec.GridSpec(fig_rows, fig_cols)

    for dim in xrange(n_dim):
        ax = fig.add_subplot(gs1[dim], projection='3d')  # , adjustable='box', aspect=1)
        subplot_latent_dimension(ax, model, data_encoded, data_encoded_modified,
                                 dim, steps, skeleton,
                                 plot_static=plot_static, plot_dynamics=plot_dynamics,
                                 verbose=verbose, **kwargs)


def subplot_latent_dimension(ax, model, data_encoded, data_encoded_modified,
                             dim, steps, skeleton=None,
                             plot_static=True, plot_dynamics=False, verbose=False, **kwargs):
    data_encoded_modified[:, dim] = np.linspace(
        min(data_encoded[:, dim]),
        max(data_encoded[:, dim]), steps)
    if verbose:
        print 'min value:', min(data_encoded_modified[:, dim]), ', max value:', max(data_encoded_modified[:, dim])
    data_reconstructed = model.decode(data_encoded_modified)

    if skeleton != None:
        if plot_static:
            skeleton.plot(ax, data_reconstructed, c='k', alpha=0.03)
        if plot_dynamics:
            plot_hand_skeleton_dynamics(ax, data_reconstructed, skeleton, cmap=cm.winter)

    #if plot_static:
    #    ax.scatter(data_reconstructed[:, 0:85:3],
    #               data_reconstructed[:, 1:85:3],
    #               data_reconstructed[:, 2:85:3], c='k', marker='o', lw=0.1, alpha=0.03)
    plt.title('Latent Dimension #' + str(dim))





def plot_compare_reconstructed_posture(data, metadata, model, frames, dropout_features=None, dropout_inputs=0,
                                       representation=rep.REPRESENTATION_XYZ, **kwargs):

    d = data.values.shape[-1]
    data_reconstructed = None
    if model is not None:
        data_zeroed = np.copy(data.values)
        if dropout_inputs > 0:
            data_zeroed[frames,np.random.choice(d, int(dropout_inputs*d), replace=False)] = 0

        if dropout_features is not None:
            dropout_features = summer_school_convert_bone_names(dropout_features)
            drop_cols_indices = metadata.get_feature_column_indices(dropout_features, representation)
            data_zeroed[frames, drop_cols_indices] = 0

        data_encoded = model.encode(data_zeroed)#data.values)
        data_reconstructed = model.decode(data_encoded)

    skeleton = skf.create_skeleton(data.columns.tolist(), metadata, representation)
    plot_reconstructed_posture(data.values, data_reconstructed,
                               frames, skeleton, **kwargs)


def plot_reconstructed_posture(data_original, data_reconstructed, frames, skeleton=None,
                               **kwargs):
    figsize = (8,8)
    if kwargs.has_key('figsize'):
        figsize = kwargs['figsize']
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    if skeleton != None:
        skeleton.plot(ax, data_original[frames], showJoints=True, c='k')
        if data_reconstructed is not None:
            skeleton.plot(ax, data_reconstructed[frames], showJoints=True, c='r')
    if kwargs.has_key('title'):
        plt.title(kwargs['title'])

    plt.show()

'''
def plot_hand_skeleton(ax, skeleton, data, c='k', cmap=None, lw=1, alpha=0.25):
    rows, cols = data.shape

    cs = None
    if cmap != None:
        cs = [cmap(v)[0:3] for v in np.linspace(0, 1, rows)]

    for row in xrange(rows):
        if cs != None:
            c = cs[row]
        for link in skeleton:
            x1 = data[row, link[0]]
            y1 = data[row, link[2]]
            z1 = data[row, link[4]]
            x2 = data[row, link[1]]
            y2 = data[row, link[3]]
            z2 = data[row, link[5]]
            ax.plot([x1, x2], [y1, y2], [z1, z2], c=c, lw=lw, alpha=alpha)
'''



def plot_hand_skeleton_dynamics(ax, data, skeleton, c='k', cmap=None, lw=1, alpha=0.25):

    if isinstance(skeleton, SkeletonQuat):
        data = skeleton.convert_data_quat_to_xyz(data)

    rows, cols = data.shape

    cs = None
    if cmap != None:
        cs = [cmap(v)[0:3] for v in np.linspace(0, 1, rows)]

    for row in xrange(1, rows):
        if cs != None:
            c = cs[row - 1]
        for col in xrange(0, cols - 3, 3):
            x1 = data[row - 1, col]
            y1 = data[row - 1, col + 1]
            z1 = data[row - 1, col + 2]
            x2 = data[row, col]
            y2 = data[row, col + 1]
            z2 = data[row, col + 2]
            ax.plot([x1, x2], [y1, y2], [z1, z2], c=c, lw=lw, alpha=alpha)



