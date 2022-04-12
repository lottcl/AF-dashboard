## MIMIC-III Data Processing

### Import Necessary Packages
import pandas as pd 
import numpy as np
from datetime import datetime
import sqlite3

### Read in procedures table from MIMIC-III
procedures = pd.read_csv('../../Data/MIMIC-III/PROCEDURES_ICD.csv.gz', compression='gzip')

### Select the subjects and admissions with CABG procedure codes
cabg = procedures.loc[procedures['ICD9_CODE'].isin([3610,3611,3612,
                                                    3613,3614,3615,
                                                    3616,3617,3619])].drop(columns=['ROW_ID',
                                                                                'SEQ_NUM',
                                                                                'ICD9_CODE']).drop_duplicates()

### Import the vital_labs_mean table from the MIMIC-Extract output file
extract = pd.read_hdf('../../Data/MIMIC-Extract/all_hourly_data.h5', 'vitals_labs_mean')

### Convert the extract table from pivot style to a flat dataframe
extract_flat = pd.DataFrame(extract.to_records())
extract_flat.columns = [hdr.replace("('", "").replace("', 'mean')", "") \
                     for hdr in extract_flat.columns]

### Select the relevant vital measurements from the extract dataframe
extract_items = extract_flat[['subject_id', 'hadm_id', 'height', 'weight', 'creatinine']]

### Merge cabg and extract_items to select CABG admissions within the extract vital measurement dataframe
cabg_extract = pd.merge(cabg, extract_items, how='left', left_on=['SUBJECT_ID', 'HADM_ID'], 
                        right_on=['subject_id','hadm_id']).drop(columns=['subject_id','hadm_id'])

### Aggregate the median measurement for each admission and convert from a pivot format to a flat dataframe
median_extract = cabg_extract.groupby(['SUBJECT_ID','HADM_ID'], as_index=False).median()
median_ext_flat = pd.DataFrame(median_extract.to_records())

### Aggregate the median measurement for each subject for imputation and convert from a pivot format to a flat dataframe
sub_med_extract = cabg_extract.groupby(['SUBJECT_ID'], as_index=False).median()
sub_med_ext_flat = pd.DataFrame(sub_med_extract.to_records())

### Merge median_ext_flat and sub_med_ext_flat and impute subject aggregated medians to null values for the same subject
# --> merge tables
sub_med_merge = pd.merge(median_ext_flat, sub_med_ext_flat, how='inner', 
                         on=['SUBJECT_ID']).drop(columns=['index_x','HADM_ID_y'])

# --> fill null values based on subject median
sub_med_merge['height_x'].fillna(sub_med_merge['height_y'], inplace=True)
sub_med_merge['weight_x'].fillna(sub_med_merge['weight_y'], inplace=True)
sub_med_merge['creatinine_x'].fillna(sub_med_merge['creatinine_y'], inplace=True)

# --> remove duplicate columns and rename
sub_med_filled = sub_med_merge.drop(columns=['index_y', 'height_y', 
                            'weight_y', 'creatinine_y']).rename(columns={'HADM_ID_x': 'HADM_ID', 'height_x': 'height', 
                                                                         'weight_x': 'weight', 
                                                                         'creatinine_x': 'creatinine'})

### Read in admissions and patients tables from MIMIC-III
admissions = pd.read_csv('../../Data/MIMIC-III/ADMISSIONS.csv.gz', compression='gzip').drop(columns=['ROW_ID'])
patients = pd.read_csv('../../Data/MIMIC-III/PATIENTS.csv.gz', compression='gzip').drop(columns=['ROW_ID'])

### Merge admissions and patients and calculate age at admission for each subject
# --> convert DOB and ADMITTIME to datetime format
admissions['ADMITTIME'] = pd.to_datetime(admissions['ADMITTIME'], format='%Y-%m-%dT%H:%M:%S').dt.date
patients['DOBTIME'] = pd.to_datetime(patients['DOB'], format='%Y-%m-%dT%H:%M:%S').dt.date

# --> merge tables
adm_pat = pd.merge(admissions, patients, how='inner', on=['SUBJECT_ID'])

# --> calculate age at admission
adm_pat['age'] = adm_pat.apply(lambda e: (e['ADMITTIME'] - e['DOBTIME']).days/365, axis=1)
adm_pat['age'] = adm_pat['age'].astype('int64')

# --> select the relevant columns
adm_pat_cols=adm_pat[['SUBJECT_ID','HADM_ID','GENDER','age']]

### Merge sub_med_merge with adm_pat_cols to determine age and gender of subjects
patient_merge = pd.merge(sub_med_filled, adm_pat_cols, how='left', on=['SUBJECT_ID', 'HADM_ID'])

### Create age groups for imputation
# --> make a db in memory for sql queries
conn = sqlite3.connect(':memory:')
# --> write the dataframe to sql
patient_merge.to_sql('patient_merge', conn, index=False)

# --> write the sql query
qry1 = '''
    select
        SUBJECT_ID,
        HADM_ID,
        height,
        weight,
        creatinine,
        GENDER,
        age,
        case
            when age <= 46 then 1
            when age between 47 and 55 then 2
            when age between 56 and 65 then 3
            when age between 66 and 75 then 4
            when age between 76 and 90 then 5
            else 6
            end as age_group
    from patient_merge
    order by 
        GENDER,
        age_group
'''

# --> run the sql query and create a pandas dataframe
age_group = pd.read_sql_query(qry1, conn)

### Calculate median height and weight by age and gender and convert from a pivot format to a flat dataframe
med_a_g = age_group.groupby(['age_group', 'GENDER'], as_index=False).median()
med_a_g_flat = pd.DataFrame(med_a_g.to_records())

### Impute height and weight by age and gender from med_a_g_flat
# --> merge tables
a_g_merge = pd.merge(age_group, med_a_g_flat, how='left', 
                     on=['age_group','GENDER']
                    ).drop(columns=['index','SUBJECT_ID_y', 'HADM_ID_y', 'creatinine_y', 'age_y', 'age_group'])

# --> fill null values based on age/gender median
a_g_merge['height_x'].fillna(a_g_merge['height_y'], inplace=True)
a_g_merge['weight_x'].fillna(a_g_merge['weight_y'], inplace=True)

# --> remove duplicate columns and rename
a_g_filled = a_g_merge.drop(columns=['height_y',
                                     'weight_y']).rename(columns={'SUBJECT_ID_x': 'subject_id',
                                                                  'HADM_ID_x': 'hadm_id', 
                                                                  'GENDER': 'gender',
                                                                  'height_x': 'height',
                                                                  'weight_x': 'weight',
                                                                  'creatinine_x': 'creatinine',
                                                                  'age_x': 'age'})

### Export the h_w_dropna dataset to impute creatinine values in R using the MICE package (see attached R code for imputation)
a_g_filled.to_csv('../../Data/MIMIC-III/na_creatinine.csv')
