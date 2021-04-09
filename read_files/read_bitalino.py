import datetime
import numpy as np
import os
import pandas as pd


def join_hour_epibox(start_file, patient, directory, h5=False):
    # get all files in path
    """
    This function takes files from Epibox acquisition and joins in a DataFrame both signals and the timestamps
    :param start_file: The first file from a batch of files to be joined
    :param patient: String with the patient ID
    :param directory: Directory where all files are located
    :param h5: whether it is supposed to be saved in h5 or csv file type
    :return: saves all files and returns the name of the last file (that will be the first in the next iteration)
    """

    if 'Bitalino_24H' not in os.listdir(work_directory):
        os.mkdir(work_directory+os.sep+'Bitalino_24H')
    save_directory = work_directory + os.sep + 'Bitalino_24H'

    dirs = sorted(os.listdir(directory))

    # only get files after start_file
    dirs = dirs[dirs.index(start_file):]
    dirs = [di for di in dirs if di[0] == 'A']

    starting_time = datetime.datetime.strptime(start_file[1:-4], '%Y-%m-%d %H-%M-%S')
    time_delta = datetime.timedelta(0, 0)
    idx_file = 0

    new_file = pd.DataFrame()

    print('STARTING NEW FILE...')

    while time_delta.total_seconds() < 60.0:

        # signal
        try:
            file_name = dirs[idx_file]
        except:
            break
        print('Join file ', file_name)

        file = np.loadtxt(directory + os.sep + file_name)

        if len(file) == 0:
            idx_file += 1
            continue
        if str(starting_time.year) not in file_name:
            new_date = input(
                'Last date is ' + str(starting_time) + ' Current date is ' + file_name + ' please insert new date')
            starting_time = datetime.datetime.strptime(new_date, '%Y-%m-%d %H-%M-%S')

        time_delta = datetime.datetime.strptime(file_name[1:-4], '%Y-%m-%d %H-%M-%S') - starting_time
        time_interval = time_delta.total_seconds() * 1000 - len(new_file)
        # new_file = np.vstack((new_file, file[:,list_indexes]))
        drift_name = 'drift_log_file_' + file_name[1:]

        drift_file = pd.read_csv(directory + os.sep + drift_name, header=None)

        try:
            new_file = pd.concat([new_file,
                                  pd.DataFrame(file[:, list_indexes], columns=dict[patient]['sensors'],
                                               index = pd.date_range(drift_file[0][0].split(' ')[1],
                                                                     periods=len(file), freq='1ms'))])
        except:
            new_file = pd.concat(
                [new_file, pd.DataFrame([[np.nan] * len(list_indexes)], columns=dict[patient]['sensors'],
                                        index = pd.date_range(drift_file[0][0].split(' ')[1],
                                                                     periods=len(file), freq='1ms'))])
        # drift

        idx_file += 1

    qq
    if h5:
        new_file.to_hdf(save_directory + 'signal_nan_' + start_file[1:-4] + '__' + file_name[1:-4] + '.h5', 'df',
                        mode='w')
    else:
        new_file.to_csv(save_directory + 'signal_nan_' + start_file[1:-4] + '__' + file_name[1:-4])
    # drift_file.to_csv('patients' + os.sep +patient + os.sep+'drift_log_file_'+start_file[1:-4]+'__'+ file_name[1:-4])
    return file_name



#start_directory = 'E:\\Patients_HSM'
start_directory = 'C:\\Users\\Mariana\\Documents\\Databases\\Epibox\\HSM\\acquisitions'
start_directory = 'C:\\Users\\Mariana\\PycharmProjects\\Epilepsy_HSM\\dash_app\\data\\Bitalino'

#start_directory = 'C:\\Users\\Mariana\\Documents\\Epilepsy\\Patients_HSM'
#patient_list = ['patient_1_3_2021']
patient_list = ['ana']
#list_indexes = [0,5,6,7,8,9,10,16,17,18,19,20,21]
list_indexes = [0,1,2,3,4,5]
dict = {}

for patient in patient_list:
    print('PATIENT ----- ' + str(patient))

    work_directory = start_directory + os.sep + patient

    if 'Bitalino' in os.listdir(work_directory):
        work_directory = os.path.join(start_directory,patient,'Bitalino')

    all_files = sorted([di for di in os.listdir(work_directory) if di[:3] == 'A20'])
    last_file = all_files[-1]
    curr_file = all_files[0]

    dict[patient] = {}

    #dict[patient]['sensors'] =  ['NSeq','EDA','PPG','EMG','AXW','AYW','AZW','EOG','ECG','PZT','AXC','AYC','AZC']
    #dict[patient]['sensors'] = ['NSeq', 'ECG', 'PZT', 'AXC', 'AYC', 'AZC']
    dict[patient]['sensors'] = ['NSeq', 'EEG', 'EEG', 'PPG', 'NSeq', 'ECG']
    while curr_file != last_file:
        print(curr_file)
        curr_file = join_hour_epibox(curr_file, patient, work_directory, h5=True)

