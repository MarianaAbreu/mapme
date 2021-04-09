
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sb

import processing.utils_signal_processing as sp

def get_diff(sig, window):

    diff_sig = sig.diff().abs().diff().abs()

    window_time = pd.date_range(sig.index[0], sig.index[-1], freq=str(window) + 'S')

    new_diff = pd.DataFrame([diff_sig.between_time(window_time[i].time(),
                                                   window_time[i + 1].time()).mean()
                             for i in range(len(window_time) - 1)], index=window_time[1:])

    return new_diff

#dir = 'E:\\Patients_HEM\\PAT_358\\nni'

def diff_from_nni():

    for pat in os.listdir('E:\\Patients_HSM\\'):

        try:
            plt.figure()
            dir = os.path.join('E:\\Patients_HSM', pat, 'nni')

            files = sorted(os.listdir(dir))

            for file in files:
                sig = pd.read_hdf(os.path.join(dir, file))

                window = 5 * 60
                new_diff = get_diff(sig, window)

                if 'Crise' in file:
                    plt.vlines(new_diff.index[len(new_diff)//2], new_diff.min(), new_diff.max())
                    c = 'Red'
                else:
                    c = 'Teal'

                plt.plot(new_diff, label=file, color=c)
                plt.legend()

            if files != []:
                plt.savefig(os.path.join(os.getcwd(), 'plotting', 'images', pat + '_'))


            plt.close()

        except:
            continue

def diff_from_features():

    features_names = ['rms_sd', 'sd_nn', 'mean_nn', 'nn50', 'pnn50', 'var', 'lf_pwr', 'hf_pwr',
                      'lf_hf', 'sd1', 'sd2', 'csi', 'csv', 'kfd', 'rec', 'det', 'lmax']

    window = 3 * 60

    for feature in features_names:

        for pat in sorted(set([file.split('_')[0] for file in os.listdir(os.path.join(os.getcwd(), 'features','HEM'))])):
            median_, mean_ = [], []
            median_value = []
            print(pat)
            files = [file for file in sorted(os.listdir(os.path.join(os.getcwd(),'features','HEM'))) if file.startswith(pat)]
            seizure_times = pd.read_csv('E:\\Patients_HEM\\PAT_358\\seizure_label', index_col=0)

            dates = [datetime.datetime.strptime(date, '%H:%M:%S\n%d-%m-%Y') for dd, date in enumerate(seizure_times['Date']) if seizure_times['Type'][dd].startswith('Crise')]

            file_dates = []
            for file in files:
                print(file)

                try:
                    sig = pd.read_hdf(os.path.join(os.getcwd(), 'features', 'HEM',file))[feature]

                    sig = sp.normalise_feats(sig, 'stand')

                    new_diff = get_diff(sig, window)
                    file_dates += [new_diff.index[0]]
                    median_ += [new_diff.median()]
                    median_value += [sig.median()]
                    mean_ += [new_diff.mean()]

                    #if 'Crise' in file:
                     #   plt.vlines(len(new_diff) // 2, 0, 1)
                      #  c = 'Red'
                    #else:
                     #   c = 'Teal'
                    #plt.plot(new_diff)
                except:
                    continue
            plt.vlines(dates, 0, 1, label='Crise')
            events = [datetime.datetime.strptime(date, '%H:%M:%S\n%d-%m-%Y') for dd, date in enumerate(seizure_times['Date']) if seizure_times['Type'][dd].startswith('Evento')]
            plt.vlines(events, 0, 1, label='Evento não epiléptico', color='green', alpha=0.7)
            plt.plot(file_dates, median_, color='teal', linewidth=3, label='median diff')
            plt.plot(file_dates, median_value, color='red', linewidth=3, label='median value')
            plt.legend()

            #plt.plot(file_dates, mean_, color='orange', linewidth=5)
            plt.savefig(os.path.join(os.getcwd(), 'plotting', 'images', str(window) + '_' + feature +'_median_' + '_png'))

            plt.close()

diff_from_features()