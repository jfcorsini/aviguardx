import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import patheffects as pe

from PIL import Image
import numpy as np
import os
import math

from math import pi, cos, sin

# https://stackoverflow.com/questions/10952060/plot-ellipse-with-matplotlib-pyplot-python

color = 'crimson'
img = Image.open("visualization/map.png")
(X, Y) = img.size

dpi = 50
figsize = X / float(dpi), Y / float(dpi)

receive_x = 567
receive_y = 803

trans_x = -4101.3
trans_y = 986.14

center_x = (trans_x + receive_x) / 2  # x-position of the center
center_y = (trans_y + receive_y) / 2  # y-position of the center

# t_rot=0      #rotation angle
t_rot = -2 / 180 * pi  # rotation angle


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

    transform_x = 440.4

    c = 5.3  # [km] distance from center to Rx
    x = bistatic_range * transform_x
    c = c * transform_x

    rad_x = (x + 2 * c) / 2 - 0.15*c
    rad_y = math.sqrt(rad_x * rad_x - c * c) - 0.1*c

    start = math.degrees(math.atan(x / c)) + 3 - 18
    stop = math.degrees(math.atan(x / c)) + 18 - 18

    Ell_rot = draw_partial_elipse(
        rad_x, rad_y, -start * pi / 180, -stop * pi / 180)
    x_ell = center_x + Ell_rot[0, :]
    y_ell = center_y + Ell_rot[1, :]

    plt.plot(receive_x, receive_y, 'x', color='salmon', markersize=20,markeredgewidth=12, alpha=0.7)
    plt.plot(receive_x, receive_y, 'x', color=color, markersize=15, markeredgewidth=6, alpha=0.7)

    plt.imshow(img)  # map of Otaniemi
    plt.axis('off')
    line, = ax.plot(x_ell, y_ell, lw=10, path_effects=[pe.Stroke(
        linewidth =20, foreground='salmon', alpha = 0.7), pe.Normal()], color=color, alpha=0.7)
    plt.grid(color='lightgray', linestyle='--')


    image_path = os.path.join(os.getcwd(), "results",
                              output_name) + '_map.jpeg'
    line.set_xdata(x_ell)
    line.set_ydata(y_ell)
    figure.canvas.draw()
    plt.savefig(image_path, bbox_inches='tight',
                transparent=True, pad_inches=0)
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
        plt.savefig(image_path, bbox_inches='tight',
                    transparent=True, pad_inches=0)
        return

    print('All predictions', predictions)
    drone_predictions = [
        p for p in predictions if p['predicted_class'] == 'drone']
    prediction_highest_score = max(drone_predictions, key=lambda x: x['score'])

    print('prediction_highest_score', prediction_highest_score)
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
    # Predicted image has 1540px of height. Prediction returns pixel value from top (0km) to bottom (5km)
    range_km = 5.0 - ((range_pixel / 1540.0) * 5.0)
    print('freq_km', freq_km)
    print('range_km', range_km)

    return main(range_km, freq_km, output_name)


if __name__ == '__main__':
    # visualize([{'predicted_class': 'drone', 'score': 0.5523254, 'coordinates': [952, 351, 1097, 517]}, {
    #           'predicted_class': 'drone', 'score': 0.5361574, 'coordinates': [1122, 1042, 1449, 1205]}], 'foo')
    main(2.5, 0, 'map_position', True)
