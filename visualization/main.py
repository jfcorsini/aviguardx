import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import os
import math
from time import sleep
import matplotlib.patheffects as pe
import matplotlib as mpl

from math import pi, cos, sin

# https://stackoverflow.com/questions/10952060/plot-ellipse-with-matplotlib-pyplot-python

color = 'mediumturquoise'
img = Image.open("visualization/map.jpg")
(X, Y) = img.size

receive_x = 390
receive_y = 437

trans_x = -1662.698
trans_y = receive_y + 78.3

center_x = (trans_x + receive_x) / 2  # x-position of the center
center_y = (trans_y + receive_y) / 2  # y-position of the center

# t_rot=0      #rotation angle
t_rot = -2.5 / 180 * pi  # rotation angle


def draw_partial_elipse(rad_x, rad_y, start, stop):
    t = np.linspace(start, stop, 100)
    Ell = np.array([rad_x * np.cos(t), rad_y * np.sin(t)])
    R_rot = np.array([[cos(t_rot), -sin(t_rot)], [sin(t_rot), cos(t_rot)]])
    Ell_rot = np.zeros((2, Ell.shape[1]))
    for i in range(Ell.shape[1]):
        Ell_rot[:, i] = np.dot(R_rot, Ell[:, i])
    return Ell_rot


def main(bistatic_range, doppler_shift, output_name):
    dpi = 50
    figsize = X / float(dpi), Y / float(dpi)
    figure, ax = plt.subplots(figsize=figsize)

    transform_x = 193.65

    c = 5.3  # [km] distance from center to Rx
    x = bistatic_range * transform_x
    c = c * transform_x

    rad_x = (x + 2 * c) / 2
    rad_y = math.sqrt(rad_x * rad_x - c * c)

    start = math.degrees(math.atan(x / c)) + 3 - 13
    stop = math.degrees(math.atan(x / c)) + 18 - 13

    Ell_rot = draw_partial_elipse(
        rad_x, rad_y, -start * pi / 180, -stop * pi / 180)
    x_ell = center_x + Ell_rot[0, :]
    y_ell = center_y + Ell_rot[1, :]

    plt.plot(receive_x, receive_y, 'x', color=color, markersize=7)

    plt.imshow(img)  # map of Otaniemi
    plt.axis('off')
    line, = ax.plot(x_ell, y_ell, lw=2, path_effects=[pe.Stroke(
        linewidth=5, foreground='lightseagreen', alpha=0.7), pe.Normal()], color=color, alpha=0.7)
    plt.grid(color='lightgray', linestyle='--')

    image_path = os.path.join(os.getcwd(), "results", output_name) + '_map.jpg'
    line.set_xdata(x_ell)
    line.set_ydata(y_ell)
    figure.canvas.draw()
    plt.savefig(image_path)
    plt.close()
    ax.clear()


def visualize(coordinates, output_name):
    image_path = os.path.join(os.getcwd(), "results", output_name) + '_map.jpg'
    if len(coordinates) < 1:
        plt.imshow(img)  # map of Otaniemi
        plt.axis('off')
        plt.savefig(image_path)
        return

    if len(coordinates) > 1:
        print('More than one drone found. Using first one only')

    coord = coordinates[0]
    if len(coord) != 4:
        print('Something is wrong with the coordinates', coord)
        return

    freq_pixel = coord[2] - coord[0]
    range_pixel = coord[3] - coord[1]

    freq_km = (freq_pixel / 24.8) - 50.0
    range_km = (range_pixel / 1540.0) * 5.0

    return main(range_km, freq_km, output_name)


if __name__ == '__main__':
    main(1.5, 0, 'map_position')
