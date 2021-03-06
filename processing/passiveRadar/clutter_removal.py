import numpy as np
import scipy.signal as signal
from scipy.linalg import solve_toeplitz
from processing.passiveRadar.signal_utils import xcorr, frequency_shift


def LS_Filter_Toeplitz(refChannel, srvChannel, filterLen, peek=10):
    '''Block east squares adaptive filter. Computes filter coefficients using
    scipy's solve_toeplitz function. This assumes the autocorrelation matrix of 
    refChannel is Hermitian and Toeplitz (i.e. wide the reference signal is
    wide sense stationary). Faster than the direct matrix inversion method but
    inaccurate if the assumptions are violated. 

    Parameters:
        refChannel:     Array containing the reference channel signal
        srvChannel:     Array containing the surveillance channel signal
        filterLen:   Length of the least squares filter (in samples)
        peek:           Number of noncausal filter taps. Set to zero for a 
                        causal filter. If nonzero, clutter estimates can depend 
                        on future values of the reference signal (this helps 
                        sometimes)
        return_filter:  Boolean indicating whether to return the filter taps

    Returns:
        srvChannelFiltered: Surveillance channel signal with clutter removed
        filterTaps:     (optional) least squares filter taps

    '''

    # shift reference channel because for some reason the filtering works
    # better when you allow the clutter filter to be noncausal
    refChannelShift = np.roll(refChannel, -1*peek)

    # compute the first column of the autocorelation matrix of ref
    autocorrRef = xcorr(refChannelShift, refChannelShift, 0,
                        filterLen + peek - 1)

    # compute the cross-correlation of ref and srv
    xcorrSrvRef = xcorr(srvChannel, refChannelShift, 0,
                        filterLen + peek - 1)

    # solve the Toeplitz least squares problem
    filterTaps = solve_toeplitz(autocorrRef, xcorrSrvRef)

    # compute clutter signal and remove from surveillance Channel
    clutter = np.convolve(refChannelShift, filterTaps, mode='full')
    clutter = clutter[0:srvChannel.shape[0]]
    srvChannelFiltered = srvChannel - clutter

    return srvChannelFiltered


def LS_Filter_Multiple(refChannel, srvChannel, filterLen, sampleRate,
                       dopplerBins=[0]):
    '''Clutter removal with least squares filter. This function allows the least
    squares filter to be applied over several frequency bins. Useful when there
    is significant clutter at nonzero doppler values.

    Parameters:
        refChannel:     Array containing the reference channel signal
        srvChannel:     Array containing the surveillance channel signal
        filterLen:      Length of the least squares filter (in samples)
        dopplerBins:    List of doppler bins to filter (default only 0Hz)

    Returns:
        srvChannelFiltered: Surveillance channel signal with clutter removed
    '''

    srvChannelFiltered = srvChannel
    for doppler in dopplerBins:
        if doppler == 0:
            srvChannelFiltered = LS_Filter_Toeplitz(refChannel,
                                                    srvChannelFiltered, filterLen)
        else:
            refMod = frequency_shift(refChannel, doppler, sampleRate)

            if refMod.shape != srvChannelFiltered.shape:
                raise ValueError(f'''Input vectors must have the same length - 
                got {refChannel.shape} and {srvChannel.shape}''')

            srvChannelFiltered = LS_Filter_Toeplitz(refMod, srvChannelFiltered,
                                                    filterLen)
    return srvChannelFiltered
