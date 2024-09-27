import numpy as np
import matplotlib.pyplot as plt

def plot(field_u, field_v, depth, subs, cvals, seapen_x, seapen_y, coral_x, coral_y, h=None):
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
    - subs: indicates the subsetting for plotting arrows (every 'subs' grid point is plotted)
    - cvals: list of depth contours to include
    - seapen_x, seapen_y: sea pen locations (x and y coordinates)
    - coral_x, coral_y: coral locations (x and y coordinates)
    - h: figure handle to plot to. If not included, a new figure will be opened.
    """

    # Calculate current speed
    if field_v is None:
        spd = field_u  # Scalar plot if only field_u is provided
        plot_arrows = False
    else:
        spd = np.sqrt(field_u**2 + field_v**2)
        plot_arrows = True

    # Create a figure
    if h is not None:
        plt.figure(h)
        plt.clf()
    else:
        plt.figure()

    # Plot current speed as a color map
    pc = plt.pcolormesh(spd.T, shading='auto')  # shading='flat' deprecated, use 'auto'
    plt.colorbar(label='Current Speed (m/s)')

    # Plot arrows for current direction, if field_v is provided
    if plot_arrows:
        X, Y = np.meshgrid(np.arange(0, field_u.shape[0], subs),
                           np.arange(0, field_u.shape[1], subs))
        plt.quiver(X, Y, field_u[::subs, ::subs].T, field_v[::subs, ::subs].T, color='k')

    # Set plot background to gray
    plt.gca().set_facecolor((0.7, 0.7, 0.7))

    # Plot bathymetry contours
    contour_set = plt.contour(depth.T, cvals, colors='w')
    plt.clabel(contour_set, inline=True, fontsize=8)  # Label contours


    # Define the limits of the grid
    min_x, max_x = 0, field_u.shape[0]
    min_y, max_y = 0, field_u.shape[1]

    # Filter sea pen locations based on the grid limits
    mask_seapen = (seapen_x >= min_x) & (seapen_x <= max_x) & (seapen_y >= min_y) & (seapen_y <= max_y)
    filtered_seapen_x = seapen_x[mask_seapen]
    filtered_seapen_y = seapen_y[mask_seapen]


    # Filter coral locations based on the grid limits
    mask_coral = (coral_x >= min_x) & (coral_x <= max_x) & (coral_y >= min_y) & (coral_y <= max_y)
    filtered_coral_x = coral_x[mask_coral]
    filtered_coral_y = coral_y[mask_coral]

    # Plot filtered sea pen locations
    plt.scatter(filtered_seapen_x, filtered_seapen_y, c='red', s=10, edgecolors='k', label='Sea Pen Locations')

    # Plot filtered coral locations
    plt.scatter(filtered_coral_x, filtered_coral_y, c='blue', s=10, edgecolors='k', label='Coral Locations')

    # Set axis limits (adjust this based on your grid's dimensions)
    plt.xlim(min_x, max_x)
    plt.ylim(min_y, max_y)

    # Add labels and legend
    plt.xlabel('Grid X')
    plt.ylabel('Grid Y')
    plt.legend()

    # Display the plot
    plt.show()

# Example usage:
# Assuming fieldU, fieldV, depth, subs, cvals, seapen_x, seapen_y, coral_x, coral_y are defined
# plot(fieldU, fieldV, depth, subs, cvals, seapen_x, seapen_y, coral_x, coral_y)


