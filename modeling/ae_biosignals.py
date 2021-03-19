
import biosppy as bp
import numpy as np
from sklearn.model_selection import train_test_split
from scipy.signal import decimate

from modeling import autoencoder


def ecg_train_ae(signal):
    """
    Function to model an autoencoder for ecg signal
    :param signal: Array with ecg signal
    :return: autoencoder output
    """

    ecg_bl = bp.signals.tools.filter_signal(signal, ftype='FIR', order=150, band='bandpass', frequency=[1, 40],
                                            sampling_rate=1000)['signal']

    ecg_bl = (ecg_bl - np.min(ecg_bl)) / (np.max(ecg_bl) - np.min(ecg_bl))

    ecg_bl = decimate(ecg_bl, 4)

    sampling_rate = 250

    window = 1 * sampling_rate

    ecg_seg = [ecg_bl[i:i + window] for i in range(0, len(ecg_bl) - window, int(window * 0.1))]

    ecg_train, ecg_test = train_test_split(np.array(ecg_seg), test_size=0.4)
    decoder, encoder = autoencoder.create_autoencoder(ecg_train, ecg_train, ecg_test, ecg_test, 'denoising_ecg',
                                                      'cosine_proximity', activ='tanh', opt='adam',
                                                      nodes=[200, 150, 70], epochs=10)
    return decoder, encoder


def ppg_ae_train(signal):
    """
    Function to model an autoencoder for ppg signal
    :param signal: Array with ppg signal
    :return: autoencoder output
    """

    ppg_bl = bp.signals.tools.filter_signal(signal, ftype='butter', order=4, band='bandpass', frequency=[1, 6],
                                            sampling_rate=1000)['signal']

    sampling_rate = 1000

    ppg_bl = (ppg_bl - np.min(ppg_bl)) / (np.max(ppg_bl) -np.min(ppg_bl))

    ppg_bl = decimate(ppg_bl, 10)

    sampling_rate = int(sampling_rate / 10)

    window = 1 * sampling_rate

    ppg_bl = [ppg_bl[i:i + window] for i in range(0, len(ppg_bl) - window, int(window * 0.1))]

    ppg_train, ppg_test = train_test_split(np.array(ppg_bl), test_size=0.4)

    decoder, encoder = autoencoder.create_autoencoder(ppg_train, ppg_train, ppg_test, ppg_test, 'denoising_ppg',
                                                      'cosine_proximity', activ='tanh', opt='adam',
                                                      nodes=[80, 60, 30], epochs=10)

    ppg_sig = np.array([ppg_bl[i:i + window] for i in range(0, len(ppg_bl) - window, window)])

    ppg_ae = decoder.predict(encoder.predict(ppg_sig))
    return ppg_ae


def eda_ae_train(signal):
    """
    Function to model an autoencoder for eda signal
    :param signal: Array with eda signal
    :return: autoencoder output
    """

    eda_bl = bp.signals.tools.filter_signal(signal, ftype='butter', order=4, band='lowpass', frequency=[3],
                                            sampling_rate=1000)['signal']

    sampling_rate = 1000

    eda_bl = (eda_bl - np.min(eda_bl)) / (np.max(eda_bl) - np.min(eda_bl))

    eda_bl = decimate(eda_bl, 10)

    sampling_rate = int(sampling_rate / 10)

    window = 1 * sampling_rate

    eda_bl = [eda_bl[i:i + window] for i in range(0, len(eda_bl) - window, int(window * 0.1))]

    eda_train, eda_test = train_test_split(np.array(eda_bl), test_size=0.4)

    decoder, encoder = autoencoder.create_autoencoder(eda_train, eda_train, eda_test, eda_test, 'denoising_ppg',
                                                      'cosine_proximity', activ='tanh', opt='adam',
                                                      nodes=[80, 60, 30], epochs=10)

    eda_sig = np.array([eda_bl[i:i + window] for i in range(0, len(eda_bl) - window, window)])

    eda_ae = decoder.predict(encoder.predict(eda_sig))

    return eda_ae
