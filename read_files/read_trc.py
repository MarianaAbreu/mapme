
from datetime import datetime
from datetime import timedelta
import neo
import os
import pandas as pd

# Adapted from here https://github.com/mne-tools/mne-python/issues/1605


def read_trc(filename, time_list, directory, save_directory, channels=None, format='h5'):

    signal = pd.DataFrame()

    if channels is None:
        channels = ['ecg', 'ECG']

    seg_micromed = neo.MicromedIO(directory + os.sep + filename).read_segment()
    start_time = seg_micromed.rec_datetime
    data = seg_micromed.analogsignals[1]
    print(start_time)
    samp_rate = int(data.sampling_rate)
    print(samp_rate)
    index_list = pd.date_range(start_time, start_time + timedelta(seconds=float(seg_micromed.t_stop)), periods = data.shape[0])

    ch_list = data.name.split(',')
    for ch in channels:
        ch_idx = [i for i in range(len(ch_list)) if ch_list[i] == ch][0]
        signal[ch] = pd.Series(data.T[ch_idx])

    if time_list is None:
        time_list = index_list
        save_directory = os.path.join(save_directory, 'signals')
    else:
        if start_time not in time_list:
            time_list.append(index_list)
            save_directory = os.path.join(save_directory, 'signals')
        else:
            if 'seizures' not in os.listdir(save_directory):
                os.mkdir(os.path.join(save_directory, 'seizures'))
            save_directory = os.path.join(save_directory, 'seizures')

    signal.to_hdf(save_directory + os.sep + filename[:-4] + '_' + datetime.strftime(start_time, '%Y-%m-%d--%H-%M-%S') + '.h5',
            'df', mode='w')
    return time_list


def read_seizures(save_directory):

    list_files = os.listdir(save_directory)
    ppp

#read_seizures('E:\Patients_HEM\PAT_358\signals')
#signal = read_trc('EEG_47717.TRC', 'E:\Patients_HEM\PAT_358', 'E:\Patients_HEM\PAT_358\signals')