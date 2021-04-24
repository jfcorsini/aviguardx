import numpy as np
import os

from processing.passiveRadar.config import getConfiguration
from processing.tracker.multitarget import multitarget_track_and_plot
from processing.passiveRadar.data_processor import process_data


def run_processing(folder_name):
    config = getConfiguration()

    image_path = os.path.join(
        os.getcwd(), "results", folder_name)
    savedir = os.path.join(os.getcwd(), "results")
    if not os.path.isdir(savedir):
        os.makedirs(savedir)

    results = process_data(config, folder_name)

    multitarget_track_and_plot(config, np.abs(results), image_path)
