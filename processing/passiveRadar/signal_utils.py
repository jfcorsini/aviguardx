''' signal_utils.py: a collection of signal processing utility functions
    for passive radar processing '''

import numpy as np
import scipy.signal as signal


def normalize(x):
    '''normalize ndarray to unit mean'''
    return x/np.mean(np.abs(x).flatten())


def deinterleave_IQ(interleavedIQ):
    '''convert interleaved IQ samples to complex64'''
    interleavedIQ = np.asarray(interleavedIQ)
    if len(interleavedIQ) % 2 != 0:
        interleavedIQ = np.resize(interleavedIQ, interleavedIQ.size - 1)

    return interleavedIQ.astype(np.float32).view(np.complex64)


def frequency_shift(x, fc, Fs, phase_offset=0):
    '''frequency shift x by fc where Fs is the sample rate of x'''
    nn = np.arange(x.shape[0], dtype=np.complex64)
    return x*np.exp(1j*2*np.pi*fc*nn/Fs + 1j*phase_offset)


def xcorr(s1, s2, nlead, nlag):
    ''' cross-correlate s1 and s2 with sample offsets from -1*nlag to nlead'''
    return signal.correlate(s1, np.pad(s2, (nlag, nlead), mode='constant'),
                            mode='valid')


def find_channel_offset(s1, s2, nd, nl):
    '''use cross-correlation to find channel offset in samples'''
    B1 = signal.decimate(s1, nd)
    B2 = np.pad(signal.decimate(s2, nd), (nl, nl), 'constant')
    xc = np.abs(signal.correlate(B1, B2, mode='valid'))
    return (np.argmax(xc) - nl)*nd


def preprocess_kerberossdr_input(arr):
    '''
    Found this solution from https://stackoverflow.com/questions/9537543/replace-nans-in-numpy-array-with-closest-non-nan-value
    '''
    mask = np.isnan(arr)
    arr[mask] = np.interp(np.flatnonzero(
        mask), np.flatnonzero(~mask), arr[~mask])

    # Clip data to avoid having overflow when multiplying too big numbers
    return np.clip(arr, -1e+10, 1e+10)
