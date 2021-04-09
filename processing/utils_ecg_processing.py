import biosppy
import numpy as np
import os
import pandas as pd
from scipy.signal import resample
from scipy.stats import pearsonr

import utils_signal_processing as usp


def _ecg_correction(filt_sig, rpeaks, mean_template, min_rp, max_rp, idxmin, idxmax):
    """
    This function calculates the euclidean distance between all signal templates and the mean template.
    The signal templates with distances above the threshold are correlated point by point with the mean
        template, to find the maximum correlation using pearson correlation.
    The template is replaced by the mean template at the point of maximum correlation.
    The previous and following points are replaced by the first and last mean_template values, respectively.
    The corrected signal is returned.

    :param filt_sig: ecg signal
    :param rpeaks: r peak locations
    :param mean_template: average template with 600ms and r peak at 200ms
    :param min_rp: distance to r peak
    :param max_rp: distance from r peak to end
    :param idxmin: start of cropped template
    :param idxmax: end of cropped template
    :return: corrected signal
    """

    delta = idxmax - idxmin # cropped mean_template length
    if rpeaks[0] - min_rp < 0:
        filt_sig = np.hstack((np.zeros(min_rp-rpeaks[0]) + filt_sig[0], filt_sig))
        rpeaks += (min_rp-rpeaks[0])
    if rpeaks[-1] + max_rp > len(filt_sig):
        filt_sig = np.hstack((filt_sig,np.zeros(max_rp - (len(filt_sig)- rpeaks[-1])) + filt_sig[-1]))


    #euclidean distance between the signal around r peak and the mean template
    euc_dist = [np.linalg.norm(mean_template - filt_sig[rpi - min_rp: rpi + max_rp]) for rpi in rpeaks]
    #threshold distance
    threshold_dist = np.mean(euc_dist) + np.std(euc_dist)

    for dl in np.argwhere(euc_dist > threshold_dist).reshape(-1):
        # template to correct
        seg = filt_sig[rpeaks[dl] - min_rp: rpeaks[dl] + max_rp]
        # padding between and after
        seg_pad = np.hstack((seg[0] + np.zeros(delta), seg, seg[-1] + np.zeros(delta)))

        # pearson correlation and maximum location
        pr = np.argmax([pearsonr(mean_template[idxmin:idxmax], seg_pad[i:i + delta])[0]
                        for i in range(int(delta / 2), len(seg_pad) - delta)]) + int(delta / 2)

        # replacing by mean template
        seg_pad[:pr - idxmin] = np.zeros(pr - idxmin) + mean_template[0]
        seg_pad[pr - idxmin: pr + delta] = mean_template[:idxmax]
        if pr + idxmax < len(seg_pad):
            seg_pad[pr + idxmax:] = np.zeros(len(seg_pad) - pr - idxmax) + mean_template[-1]

        filt_sig[rpeaks[dl] - min_rp: rpeaks[dl] + max_rp] = seg_pad[delta:-delta]

    return filt_sig


def ecg_correction(sig, rpeaks = None, mean_template= None, sampling_rate=1000, show=False):

    min_rp = int(0.2 * sampling_rate)
    max_rp = int(0.4 * sampling_rate)
    idxmin = int(0.1 * sampling_rate)
    idxmax = int(0.4 * sampling_rate)
    delta = idxmax - idxmin

    filt_sig = biosppy.signals.tools.filter_signal(sig, ftype='FIR', frequency=[5, 20], band='bandpass', order=150,
                                                   sampling_rate=sampling_rate)['signal']
    if rpeaks is None:
        rpeaks, = biosppy.signals.ecg.hamilton_segmenter(filt_sig, sampling_rate=sampling_rate)
        rpeaks, = biosppy.signals.ecg.correct_rpeaks(filt_sig, rpeaks, sampling_rate, tol=0.05)

    if mean_template is None:
        templates = biosppy.signals.ecg.extract_heartbeats(filt_sig, rpeaks,
                                                              sampling_rate=sampling_rate)['templates']
        mean_template = usp.clean_outliers(templates).mean(axis=0)

    filt_sig = _ecg_correction(filt_sig, rpeaks, mean_template, min_rp, max_rp, idxmin, idxmax)

    rpeaks, = biosppy.signals.ecg.hamilton_segmenter(filt_sig, sampling_rate=sampling_rate)
    rpeaks, = biosppy.signals.ecg.correct_rpeaks(filt_sig, rpeaks, sampling_rate, tol=0.05)
    return filt_sig, rpeaks


def get_nn_intervals(sig, rpeaks=None, sampling_rate=256):

    if rpeaks is None:
        filt_sig = biosppy.signals.tools.filter_signal(sig, ftype='FIR', frequency=[5, 20], band='bandpass', order=150,
                                                   sampling_rate=sampling_rate)['signal']
        rpeaks, = biosppy.signals.ecg.hamilton_segmenter(filt_sig, sampling_rate=sampling_rate)
        rpeaks, = biosppy.signals.ecg.correct_rpeaks(filt_sig, rpeaks, sampling_rate, tol=0.05)

    rpeaks = np.array(rpeaks, dtype=float)

    nni = np.diff(rpeaks)
    nni = resample(nni, len(nni) * 4)

    return nni


def get_hr_rate(rpeaks, sampling_rate=256):

    hr_idx, hr = biosppy.signals.tools.get_heart_rate(beats=rpeaks,
                                                      sampling_rate=sampling_rate,
                                                      smooth=True,
                                                      size=3)

    return hr_idx, hr


def ecg_processing(sig, sampling_rate=256, correction=True, hr=False):

    if correction:
        sig, rpeaks = ecg_correction(sig, sampling_rate=sampling_rate)
    else:
        rpeaks = None

    nni = get_nn_intervals(sig, rpeaks, sampling_rate=sampling_rate)

    if hr:
        hr_idx, hr = get_hr_rate(rpeaks, sampling_rate=sampling_rate)

    return nni

