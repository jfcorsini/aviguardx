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

dpi = 50
figsize = X / float(dpi), Y / float(dpi)

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


def main(bistatic_range, doppler_shift, output_name, show=False):
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

    image_path = os.path.join(os.getcwd(), "results",
                              output_name) + '_map.jpeg'
    line.set_xdata(x_ell)
    line.set_ydata(y_ell)
    figure.canvas.draw()
    plt.savefig(image_path)
    if show:
        plt.show()
    plt.close()
    ax.clear()


def visualize(predictions, output_name):
    image_path = os.path.join(os.getcwd(), "results",
                              output_name) + '_map.jpeg'
    if len(predictions) < 1:
        figure, ax = plt.subplots(figsize=figsize)
        plt.imshow(img)  # map of Otaniemi
        plt.axis('off')
        figure.canvas.draw()
        plt.savefig(image_path)
        return

    print('All predictions', predictions)
    drone_predictions = [
        p for p in predictions if p['predicted_class'] == 'drone']
    prediction_highest_score = max(drone_predictions, key=lambda x: x['score'])

    coord = prediction_highest_score['coordinates']
    if len(coord) != 4:
        print('Something is wrong with the coordinates', coord)
        return

    [left, top, right, bottom] = coord
    # Take position in the middle between left and right coordinate
    freq_pixel = left + ((right - left) / 2)

    # Take position in the middle between top and bottom coordinate
    range_pixel = bottom + ((top - bottom)/2)

    # Predicted image has 2480px of width and frequency starts in -50
    freq_km = ((freq_pixel / 2480.0) * 100.0) - 50.0
    # Predicted image has 1540px of height and position starts in 0
    range_km = ((range_pixel / 1540.0) * 5.0)

    return main(range_km, freq_km, output_name)


if __name__ == '__main__':
    main(2.5, 0, 'map_position', True)
