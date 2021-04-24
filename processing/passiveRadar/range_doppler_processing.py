''' range_doppler_processing.py: a collection of algorithms for computing the
    cross-ambiguity function for passive radar '''

import numpy as np
import scipy.signal as signal
from scipy.fftpack import fft   # use scipy's fftpack since np.fft.fft
# automatically promotes input data to complex128


def fast_xambg(refChannel,
               srvChannel,
               rangeBins,
               freqBins,
               inputLen,
               window):
    ''' Fast Cross-Ambiguity Fuction (frequency domain method)

    Args:
        refChannel: Reference channel data

        srvChannel: Surveillance channel data

        rangeBins:  Number of range bins to compute

        freqBins:   Number of doppler bins to compute (should be power of 2)

        inputLen:   Expected length of the input data in samples. If the inputs
                    are shorter than this, they are extended by zero padding.

        window:     Apodization window. Can either be an ndarray of the same
                    shape as the input data, or a string/tuple to be used as
                    the 'window' parameter in scipy.signal.get_window().
    Returns:
        ndarray of dimensions (nf, nlag+1, 1) containing the cross-ambiguity
        surface. third dimension added for easy stacking in dask.

    '''

    n_chunk, chunk_length = refChannel.shape
    # calculate decimation factor
    ndecim = int(chunk_length/freqBins)

    # complex conjugate of the second input vector
    srvChannelConj = np.conj(srvChannel)

    # precompute short FIR filter for decimation (all ones filter with length
    # equal to the decimation factor)
    dtaps = np.ones((ndecim + 1,))

    dfilt = signal.dlti(dtaps, 1)
    # pre-allocate space for the result

    xambg = np.zeros((rangeBins+1, freqBins, n_chunk), dtype=np.complex64)

    # loop over range bins
    window_refChannel = refChannel * window

    # srvChannelConj_double has shape n_chunk, 2*chunk_length
    # It duplicates every data chunk without extra copy.
    # We can slice part of it in the for loop instead of rolling the array.
    srvChannelConj_double = np.lib.stride_tricks.as_strided(srvChannelConj,
                                                            shape=(
                                                                n_chunk, 2, chunk_length),
                                                            strides=(srvChannelConj.strides[0], 0, srvChannelConj.strides[1]))
    srvChannelConj_double = srvChannelConj_double.reshape(n_chunk, -1)
    for k, lag in enumerate(np.arange(-1*rangeBins, 1)):
        channelProduct = srvChannelConj_double[:, -
                                               lag: -lag+chunk_length] * window_refChannel

        xambg[k] = signal.decimate(
            channelProduct, ndecim, ftype=dfilt, axis=1).T
    xambg = np.swapaxes(xambg, 0, 1)
    # take the FFT along the first axis (Doppler)
    xambg = np.fft.fftshift(fft(xambg, axis=0), axes=0)
    return xambg
