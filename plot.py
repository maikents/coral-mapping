import numpy as np
import matplotlib.pyplot as plt

def plot(field_u, field_v, depth, subs, cvals,h=None):
    """
    Plots a color map of current speed overlaid with arrows indicating
    current speed and direction, and selected bathymetry contours.
    If the second component is empty, the first component is plotted as a scalar
    field (with no arrow plot).

    Parameters:
    - field_u: the U current components
    - field_v: the V current components. If empty, field_u will be plotted as a
               scalar field.
    - depth: the bathymetry field
    - subs: indicates the subsetting for plotting arrows (every 'subs' grid
            point is plotted)
    - cvals: list of depth contours to include
    - h: figure handle to plot to. If not included, a new figure will be opened.
    """

    if field_v is None:
        spd = field_u
        plot_arrows = False
    else:
        spd = np.sqrt(field_u**2 + field_v**2)
        plot_arrows = True

    if h is not None:
        plt.figure(h)
        plt.clf()
    else:
        plt.figure()

    # Create a reference to the pcolormesh object
    pc = plt.pcolormesh(spd.T, shading='flat')
    plt.colorbar()

    if plot_arrows:
        X, Y = np.meshgrid(np.arange(0, field_u.shape[0], subs),
                           np.arange(0, field_u.shape[1], subs))
        plt.quiver(X, Y, field_u[::subs, ::subs].T, field_v[::subs, ::subs].T, color='k')

    plt.gca().set_facecolor((0.7, 0.7, 0.7))

    # Create a reference to the contour set
    contour_set = plt.contour(depth.T, cvals, colors='w')

    # Extract contour values and handles
    contour_values = contour_set.levels
    contour_handles = contour_set.collections

    # # Set color limits
    # pc.set_clim(vmin, vmax)
  
    plt.show()



# @ Example usage:
# Assuming fieldU, fieldV, depth, subs, cvals are defined
# plot_with_contours(fieldU, fieldV, depth, subs, cvals)