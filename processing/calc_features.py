import biosppy
import multiprocessing as mp
import numpy as np
import os
import pandas as pd
from pyhrv.tools import nn_intervals
from scipy.signal import resample
import time


import hrv_features


main_dir = os.path.join(os.getcwd(), 'data')


features_names = ['rms_sd', 'sd_nn', 'mean_nn', 'nn50', 'pnn50', 'var', 'lf_pwr', 'hf_pwr',
                  'lf_hf', 'sd1', 'sd2', 'csi', 'csv', 'kfd', 'rec', 'det', 'lmax']


def f(signal):
    return hrv_features.hrv_features(signal)


if __name__ == '__main__':
    """
    Example Script - Computing all HRV parameters of pyHRV
    """
    # Import

    start_time = time.time()

    for patient in os.listdir('E:\\Patients_HEM'):


        try:
            base_dir = [cris for cris in os.listdir(os.path.join('E:\\Patients_HEM', patient, 'nni'))]
        except:
            base_dir = []
            print('No Baseline ', patient )

        if len(base_dir) >= 1:

            for crise in sorted(base_dir):

                sig = pd.read_hdf(os.path.join('E:\\Patients_HEM', patient, 'nni', crise))

                if sig.empty:
                    continue

                diff_idx = np.diff(sig.index)
                idx = np.hstack([0, np.argwhere(diff_idx!= diff_idx[0]).reshape(-1), -1])

                nni = sig['nni'].values

                df_features = pd.DataFrame()

                with mp.Pool(mp.cpu_count()) as p:

                    features = np.vstack(p.map(f,[nni[i:i+180] for i in range(0, len(nni)-180, 60)]))

                index_df = pd.date_range(sig.index[0], sig.index[-1], periods=len(features))

                df_features = pd.concat((df_features, pd.DataFrame(features, index=index_df, columns=features_names)))

                df_features.to_hdf('p'+ patient.split('t')[-1] +'_' + crise + '_hrv_features', 'df', mode='w')

    print('Total time for calculate features ', time.time()-start_time)