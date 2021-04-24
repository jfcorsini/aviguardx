import numpy as np
import zarr
import dask.array as da
import scipy.signal as signal

from processing.passiveRadar.signal_utils import find_channel_offset, \
    deinterleave_IQ, preprocess_kerberossdr_input
from processing.passiveRadar.clutter_removal import LS_Filter_Multiple
from processing.passiveRadar.range_doppler_processing import fast_xambg


def process_data(config, folder_name):
    file1 = './data/' + folder_name + '/output1'
    file2 = './data/' + folder_name + '/output2'

    refInputFile = preprocess_kerberossdr_input(np.fromfile(
        open(file1), dtype=np.float32))
    svrInputFile = preprocess_kerberossdr_input(np.fromfile(
        open(file2), dtype=np.float32))

    # get the first few hundred thousand samples of data and use it to
    #  estimate the offset between the channels
    refc1 = refInputFile[0:20*config['cpi_samples']]
    srvc1 = svrInputFile[0:20*config['cpi_samples']]

    offset = find_channel_offset(refc1, srvc1, 1, 5000000)

    # Convert to dask array after de-interleave IQ samples
    if offset > 0:
        ref_data = da.from_array(deinterleave_IQ(refInputFile[offset:]),
                                 chunks=(config['input_chunk_length']//2,))
        srv_data = da.from_array(deinterleave_IQ(svrInputFile[:-offset]),
                                 chunks=(config['input_chunk_length']//2,))
    elif offset < 0:
        ref_data = da.from_array(deinterleave_IQ(refInputFile[:-offset]),
                                 chunks=(config['input_chunk_length']//2,))
        srv_data = da.from_array(deinterleave_IQ(svrInputFile[offset:]),
                                 chunks=(config['input_chunk_length']//2,))
    else:
        ref_data = da.from_array(deinterleave_IQ(refInputFile),
                                 chunks=(config['input_chunk_length']//2,))
        srv_data = da.from_array(deinterleave_IQ(svrInputFile),
                                 chunks=(config['input_chunk_length']//2,))

    print(f"Corrected a sample offset of {offset} samples between channels")

    # trim the data to an integer number of block lengths
    N_chunks_ref = ref_data.shape[0] // (config['input_chunk_length']//2)
    N_chunks_srv = srv_data.shape[0] // (config['input_chunk_length']//2)
    N_chunks = min(N_chunks_ref, N_chunks_srv, config['num_frames']) - 1
    ref_data = ref_data[0:N_chunks*config['input_chunk_length']//2]
    srv_data = srv_data[0:N_chunks*config['input_chunk_length']//2]

    # apply the block least squares filter
    srv_cleaned = da.map_blocks(LS_Filter_Multiple,
                                ref_data,
                                srv_data,
                                config['num_range_cells'],
                                config['IF_sample_rate'],
                                # remove clutter at 0Hz, +/-1Hz, +/-2Hz
                                [0, 1, -1, 2, -2],
                                dtype=np.complex64,
                                chunks=(config['output_chunk_length'],))

    if config['overlap_cpi']:
        # pad chunks with overlapping sections
        ref_data = da.overlap.overlap(
            ref_data, depth=config['window_overlap'], boundary=0)
        srv_cleaned = da.overlap.overlap(
            srv_cleaned, depth=config['window_overlap'], boundary=0)

    # Compute Dask operation and convert to Numpy array
    ref_data = ref_data.compute()
    srv_cleaned = srv_cleaned.compute()

    # reshape to N_chunks, chunk_length
    ref_data = ref_data.reshape(N_chunks, -1)
    srv_cleaned = srv_cleaned.reshape(N_chunks, -1)

    window = signal.get_window(('kaiser', 5.0), config['cpi_samples'])

    # use the cross-ambiguity function to compute range-doppler maps
    xambg = fast_xambg(ref_data,
                       srv_cleaned,
                       config['num_range_cells'],
                       config['num_doppler_cells'],
                       config['cpi_samples'],
                       window)

    return xambg
