import yaml
import fractions
import numpy as np


def getConfiguration():
    '''sets up parameters for passive radar processing'''

    config_file = open('processing/PRconfig.yaml', 'r')
    config = yaml.safe_load(config_file)
    config_file.close()

    # get the cpi length in samples - should be a power of 2 for computational
    # efficiency.
    config['cpi_samples'] = nextpow2(config['input_sample_rate']
                                     * config['cpi_seconds_nominal'])

    # Override because sample
    config['IF_sample_rate'] = config['input_sample_rate']

    # as a result of the approximate rational resampling, the actual cpi
    # duration differs from the nominal value by a small amount.
    config['cpi_seconds_actual'] = config['cpi_samples'] \
        / config['input_sample_rate']
    config['doppler_cell_width'] = 1 / config['cpi_seconds_actual']

    # the width of each range cell in km
    config['range_cell_width'] = 2.998e5 / config['IF_sample_rate']

    # number of range cells needed to obtaine the desired range
    config['num_range_cells'] = round(config['max_range_nominal']
                                      / config['range_cell_width'])

    # true bistatic range
    config['max_range_actual'] = config['num_range_cells'] \
        * config['range_cell_width']

    # number of doppler cells - is a power of 2 for computational efficiency
    config['num_doppler_cells'] = nearestpow2(2 * config['max_doppler_nominal']
                                              * config['cpi_seconds_actual'])

    # actual maximum doppler shift
    config['max_doppler_actual'] = config['num_doppler_cells'] \
        / (2 * config['cpi_seconds_actual'])

    # get the chunk sizes to be used for processing. This depends on whether
    # the CPI sections overlap
    if config['overlap_cpi']:
        config['input_chunk_length'] = int(np.floor(config['cpi_samples']))
        if config['input_chunk_length'] % 2 != 0:
            config['input_chunk_length'] -= 1
        config['output_chunk_length'] = config['cpi_samples'] // 2
        config['window_overlap'] = config['cpi_samples'] // 4
        config['frame_interval'] = config['cpi_seconds_actual'] / 2
    else:
        config['input_chunk_length'] = int(np.floor(config['cpi_samples']) * 2)
        config['output_chunk_length'] = config['cpi_samples']
        config['frame_interval'] = config['cpi_seconds_actual']

    config['range_doppler_map_fname'] = config['output_fname'] + '.zarr'

    config['meta_fname'] = config['output_fname'] + '.npz'

    return config


def nextpow2(i):
    n = 1
    while n < i:
        n *= 2
    return n


def nearestpow2(i):
    nextp2 = nextpow2(i)
    prevp2 = nextp2 // 2
    if (nextp2 - i) < (i - prevp2):
        return nextp2
    else:
        return prevp2
