import os
import pandas as pd
#import read_bitalino
from importlib import reload

import read_trc

reload(read_trc)

print(os.listdir('E:\Patients_HEM\PAT_358'))

time_list = None

for file in sorted(os.listdir('E:\Patients_HEM\PAT_358')):
    #print(time_list)
    if file.endswith('TRC'):
        time_list = read_trc.read_trc(file, time_list, 'E:\Patients_HEM\PAT_358', 'E:\Patients_HEM\PAT_358')