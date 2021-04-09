import datetime
import multiprocessing as mp
import numpy as np
import os
import pandas as pd


import utils_ecg_processing as uep


def sig_to_nni(list):

    file = list[0]
    dir = list[1]
    sampling_rate = list[2]

    sig = pd.read_hdf(os.path.join(dir,'Crise') + os.sep + file)

    if 'HEM' in dir:
        date = file.split('_')[-1].split('.')[0]
        start_date = datetime.datetime.strptime(date, '%Y-%m-%d--%H-%M-%S')
        end_time = datetime.timedelta(milliseconds=len(sig) * 1000 / sampling_rate) + start_date

    elif 'HSM' in dir:
        date = str(file)
        start_date = sig.index[0]
        end_time = sig.index[-1]

    sig = sig['ECG'].values

    nni = uep.ecg_processing(sig, sampling_rate=sampling_rate)
    index = pd.date_range(start_date, end_time, periods=len(nni))

    nni_df = pd.DataFrame(nni, columns=['nni'], index=index)

    nni_df.to_hdf(os.path.join(dir, 'nni', 'nni_' + date), 'df', mode='w')



def all_files_process(dir, save_dir='',save=True):

    list_files = os.listdir(dir)

    for file in list_files:
        sig = pd.read_hdf(dir + os.sep + file)['ECG'].values



        date = file.split('_')[-1].split('.')[0]
        start_date = datetime.datetime.strptime(date, '%Y-%m-%d--%H-%M-%S')
        end_time =  datetime.timedelta(milliseconds=len(sig)*1000/256)+start_date
        nni = uep.ecg_processing(sig, sampling_rate=256)
        index = pd.date_range(start_date, end_time, periods=len(nni))

        nni_df = pd.DataFrame(nni, ['nni'], index=index)
        if save:
            nni_df.to_hdf(os.path.join(save_dir,'nni_'+start_date))
    qqq
    return nni


if __name__ == '__main__':

    # dir = 'E:\\Patients_HEM\\PAT_358'
    for pat in os.listdir('E:\Patients_HSM\\'):
        dir = 'E:\Patients_HSM\\' + pat

        try:

            try:
                os.mkdir(os.path.join(dir, 'nni'))
            except:
                'Path exists'

            with mp.Pool(mp.cpu_count()) as p:
                p.map(sig_to_nni,[[file, dir, 1000] for file in os.listdir(os.path.join(dir, 'Crise'))])
        except:
            continue

#

#dir = 'E:\Patients_HSM\Patient101'

#all_files_process(os.path.join(dir, 'Baseline'),os.path.join(dir, 'nni'))
#
