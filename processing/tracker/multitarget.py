''' Kalman filter based target tracker that can handle multiple targets'''

import numpy as np
import matplotlib.pyplot as plt
import zarr
import os
import sys
from tqdm import tqdm

from processing.passiveRadar.config import getConfiguration
from processing.passiveRadar.target_detection import multitarget_tracker
from processing.passiveRadar.target_detection import CFAR_2D


def parse_args():

    parser = argparse.ArgumentParser(
        description="PASSIVE RADAR TARGET TRACKER")

    parser.add_argument(
        '--config',
        required=True,
        type=str,
        help="Path to the configuration file")

    parser.add_argument(
        '--mode',
        choices=['video', 'frames', 'plot'],
        default='plot',
        help="Output a video, video frames or a plot."
    )

    return parser.parse_args()


def multitarget_track_and_plot(config, xambg, image_path):
    Nframes = xambg.shape[2]
    print("Applying CFAR filter...")
    # CFAR filter each frame using a 2D kernel
    CF = np.zeros(xambg.shape)
    for i in tqdm(range(Nframes)):
        CF[:, :, i] = CFAR_2D(xambg[:, :, i], 18, 4)

    print("Applying Kalman Filter...")
    # run the target tracker
    N_TRACKS = 10
    tracker_history = multitarget_tracker(CF,
                                          [config['max_doppler_actual'],
                                              config['max_range_actual']],
                                          N_TRACKS)

    # find the indices of the tracks where there are confirmed targets
    tracker_status = tracker_history['status']
    tracker_status_confirmed_idx = np.nonzero(tracker_status != 2)

    # get the range and doppler values for each target track
    tracker_range = np.squeeze(tracker_history['estimate'][:, :, 0]).copy()
    tracker_doppler = np.squeeze(tracker_history['estimate'][:, :, 1]).copy()

    # if the target is uncorfirmed change the range/doppler values to nan
    tracker_range[tracker_status_confirmed_idx] = np.nan
    tracker_doppler[tracker_status_confirmed_idx] = np.nan

    fig = plt.figure(figsize=(16, 10))
    plt.xlim(left=-50, right=50)
    plt.ylim(bottom=0, top=5)
    plt.scatter(tracker_doppler, tracker_range, marker='.')
    plt.axis('off')
    plt.savefig(image_path + ".jpeg", dpi=200, bbox_inches='tight',
                transparent=True, pad_inches=0)
    plt.close()

    fig = plt.figure(figsize=(16, 10))
    plt.xlim(left=-50, right=50)
    plt.ylim(bottom=0, top=5)
    plt.scatter(tracker_doppler, tracker_range, marker='.')
    plt.savefig(image_path + "_labeled.jpeg", dpi=200)
    plt.close()
