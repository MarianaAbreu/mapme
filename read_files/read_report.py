
from collections import OrderedDict
import docx as dc
import datetime
import json
import os
import pandas as pd

dir = 'E:\Patients_HEM\PAT_358'

doc_dir = [file for file in os.listdir(dir) if file.endswith('.docx')][0]

# get word document
doc = dc.Document(os.path.join(dir, doc_dir))

# find table that has 'V/S', which is the table with the dates
try:
    doc_table = [table for table in doc._body.tables if [table for cell in table._cells if 'V/S' in cell.text]!=[]][0]
except:
    print('V/S is not in tables, please check your report.')
    doc_table = None


seizure_times = pd.DataFrame()

seizure_times_type, seizure_times_date, seizure_times_state, seizure_times_class = [], [], [], []

for cl, cell in enumerate(doc_table._cells):

    if ('Evento' in cell.text) or ('Crise' in cell.text):
        try:
            date = datetime.datetime.strptime(doc_table._cells[cl + 1].text, '%H:%M:%S\n%d-%m-%Y')
        except:
            date = None
        if date:
            seizure_times_type += [cell.text]
            seizure_times_date += [doc_table._cells[cl + 1].text]
            seizure_times_state += [doc_table._cells[cl + 2].text]
            if doc_table._cells[cl + 3].text == doc_table._cells[cl + 2].text:
                idx = cl + 4
            else:
                idx = cl + 3
            seizure_times_class += [doc_table._cells[idx].text]

seizure_times['Type'] = seizure_times_type
seizure_times['Date'] = seizure_times_date
seizure_times['Class'] = seizure_times_class
seizure_times['State'] = seizure_times_state

seizure_times.to_csv(os.path.join(dir, 'seizure_label'), columns = seizure_times.columns)



#json.dumps(seizure_times, open(os.path.join(dir,'seizure_times.json'),'w'), sort_keys=True, indent=4)