## MIMIC-III Data Processing Continued

### Import Necessary Packages
import pandas as pd 
import numpy as np
import sqlite3

#### Read in the dataset with imputed creatinine values
imputed = pd.read_csv('../../Data/MIMIC-III/imp_creatinine.csv')

### Calculate eGFR from creatinine, gender, and age in SQL
# --> make a db in memory for sql queries
conn = sqlite3.connect(':memory:')

# --> write the dataframe to sql
imputed.to_sql('imputed', conn, index=False)

# --> create a sql function for exponents
def sqlite_power(x,n):
    return x**int(n)
conn.create_function("power", 2, sqlite_power)

# --> write the sql query to calculate eGFR
qry1 = '''
    select
        subject_id,
        hadm_id,
        height,
        weight,
        gender,
        age,
        creatinine,
        case 
            when gender = "F" and creatinine <= 0.7 then 144*(power((creatinine/0.7),-0.329))*(power(0.993,age))
            when gender = "F" and creatinine > 0.7 then 144*(power((creatinine/0.7),-1.209))*(power(0.993,age))
            when gender = "M" and creatinine <= 0.9 then 141*(power((creatinine/0.7),-0.411))*(power(0.993,age))
            else 141*(power((creatinine/0.7),-1.209))*(power(0.993,age))
            end as eGFR
    from imputed
    order by 
        subject_id, 
        hadm_id
'''

# --> run the sql query and create a pandas dataframe
egfr_calc = pd.read_sql_query(qry1, conn)

### Read in diagnoses and notes tables from MIMIC-III
diagnoses = pd.read_csv('../../Data/MIMIC-III/DIAGNOSES_ICD.csv.gz', compression='gzip').drop(columns=['ROW_ID', 'SEQ_NUM'])
notes = pd.read_csv('../../Data/MIMIC-III/NOTEEVENTS.csv.gz', compression='gzip', usecols=['SUBJECT_ID', 'HADM_ID', 'CATEGORY', 'ISERROR', 'TEXT'])
disch_notes = notes.loc[(notes['CATEGORY']=="Discharge summary")&
                        ((notes['ISERROR'].isnull())|
                         (notes['ISERROR']==0))].drop(columns=['CATEGORY', 'ISERROR'])
procedures = pd.read_csv('../../Data/MIMIC-III/PROCEDURES_ICD.csv.gz', compression='gzip')
admissions = pd.read_csv('../../Data/MIMIC-III/ADMISSIONS.csv.gz', compression='gzip').drop(columns=['ROW_ID'])

### Merge egfr_calc and diagnoses, procedures, and admissions to get the necessary information for the risk score indicators
adm = admissions[['SUBJECT_ID', 'HADM_ID', 'ADMISSION_TYPE']]
cabg_ind = pd.merge(pd.merge(pd.merge(pd.merge(egfr_calc, diagnoses, how='left', left_on=['subject_id','hadm_id'], 
                                               right_on=['SUBJECT_ID', 'HADM_ID']),
                                      procedures, how='left', on=['SUBJECT_ID', 'HADM_ID']),
                             adm, how='left', left_on=['subject_id','hadm_id'], right_on=['SUBJECT_ID', 'HADM_ID']), 
                    notes, how='left', left_on=['subject_id','hadm_id'], 
                    right_on=['SUBJECT_ID', 'HADM_ID']).drop(columns=['SUBJECT_ID',
                                                                      'HADM_ID',
                                                                      'ROW_ID',
                                                                      'SEQ_NUM']).rename(columns={'ICD9_CODE_x': 'd_ICD',
                                                                                                  'ICD9_CODE_y': 'p_ICD',
                                                                                                  'TEXT': 'notes',
                                                                                                  'ADMISSION_TYPE': 'type'})

### Create indicators for diagnoses and procedures
# --> Congestive Heart Failure/Left Ventricular Dysfunction (CHADS2)
cabg_ind['chf'] = np.where(cabg_ind['d_ICD'].isin(['4280','4281']),1,0)
# --> Hypertension (CHADS2)
cabg_ind['hbp'] = np.where(cabg_ind['d_ICD'].isin(['4010','4011','4019']),1,0)
# --> Diabetes Mellitus (CHADS2)
cabg_ind['dm'] = np.where(cabg_ind['d_ICD'].isin(['24900', '24901', '24910', '24911', '24920', '24921', '24930', '24931', '24940', '24941', '24950', '24951', '24960', 
                                                  '24961', '24970', '24971', '24980', '24981', '24990', '24991', '25000', '25001', '25002', '25003', '25010', '25011', 
                                                  '25012', '25013', '25020', '25021', '25022', '25023', '25030', '25031', '25032', '25033', '25040', '25041', '25042', 
                                                  '25043', '25050', '25051', '25052', '25053', '25060', '25061', '25062', '25063', '25070', '25071', '25072', '25073', 
                                                  '25080', '25081', '25082', '25083', '25090', '25091', '25092', '25093', '64800', '64801', '64802', '64803', '64804'
                                                 ]),1,0)
# --> Stroke/Transient Ischemic Attack/Thromboembolism (CHADS2)
cabg_ind['stroke'] = np.where(cabg_ind['d_ICD'].isin(['V1254']),1,0)
# --> Vascular Disease (CHADS2)
cabg_ind['vd'] = np.where(cabg_ind['d_ICD'].isin(['393', '3940', '3941', '3942', '3949', '3950', '3951', '3952', '3959', '3960', '3961', '3962', '3963', '3968', 
                                                  '3969', '3970', '3971', '3979', '3980', '4010', '4011', '4019', '40200', '40201', '40210', '40211', '40290', 
                                                  '40291', '40300', '40310', '40311', '40390', '40391', '40400', '40401', '40402', '40403', '40410', '40411', '40412', 
                                                  '40413', '40490', '40491', '40492', '40493', '40501', '40509', '40511', '40519', '40591', '40599', '41000', '41001', 
                                                  '41002', '41010', '41011', '41012', '41020', '41021', '41022', '41030', '41031', '41032', '41040', '41041', '41042', 
                                                  '41050', '41051', '41052', '41060', '41061', '41062', '41070', '41071', '41072', '41080', '41081', '41082', '41090', 
                                                  '41091', '41092', '4110', '4111', '41181', '41189', '412', '4130', '4131', '4139', '41400', '41401', '41402', 
                                                  '41403', '41404', '41405', '41406', '41407', '41410', '41411', '41412', '41419', '4142', '4143', '4144', '4148', 
                                                  '4149', '4150', '41511', '41512', '41513', '41519', '4160', '4161', '4162', '4168', '4169', '4170', '4171', '4178', 
                                                  '4179', '4200', '42090', '42091', '42099', '4210', '4211', '4219', '4220', '42290', '42291', '42292', '42293', 
                                                  '42299', '4230', '4231', '4232', '4233', '4238', '4239', '4240', '4241', '4242', '4243', '42490', '42491', '42499', 
                                                  '4250', '42511', '42518', '4252', '4253', '4254', '4255', '4257', '4258', '4259', '4260', '42610', '42611', '42612', 
                                                  '42613', '4262', '4263', '4264', '42650', '42651', '42652', '42653', '42654', '4266', '4267', '42681', '42682', 
                                                  '42689', '4269', '4270', '4271', '4272', '42731', '42732', '42741', '42742', '4275', '42760', '42761', '42769', 
                                                  '42781', '42789', '4279', '4280', '4281', '42820', '42821', '42822', '42823', '42830', '42831', '42832', '42840', 
                                                  '42841', '42842', '42843', '4289', '4290', '4291', '4292', '4293', '4294', '4295', '4296', '42971', '42979', '42981', 
                                                  '42982', '42983', '42989', '4299', '43390', '430', '431', '4320', '4321', '4329', '43300', '43301', '43310', '43320', 
                                                  '43321', '43330', '43331', '43380', '43381', '43390', '43391', '43400', '43401', '43410', '43411', '43490', '43491', 
                                                  '4350', '4351', '4352', '4353', '4358', '436', '4370', '4371', '4372', '4373', '4374', '4375', '4376', '4377', '4378',
                                                  '4379', '4380', '43810', '43811', '43812', '43813', '43814', '43819', '43820', '43821', '43822', '43830', '43831',
                                                  '43840', '43841', '43842', '43850', '43851', '43852', '43853', '4386', '4387', '43881', '43882', '43883', '4400', 
                                                  '4401', '44020', '44021', '44022', '44023', '44024', '44029', '44030', '44031', '44032', '4404', '4408', '4409', 
                                                  '44100', '44101', '44102', '44103', '4411', '4412', '4413', '4414', '4415', '4416', '4417', '4419', '4420', '4421', 
                                                  '4422', '4423', '44281', '44282', '44283', '44284', '44289', '4429', '4430', '4431', '44321', '44322', '44323', 
                                                  '44324', '44329', '44381', '44389', '4439', '44401', '44409', '4441', '44421', '4422', '44481', '44489', '4449', 
                                                  '44501', '44502', '44581', '44589', '4460', '4461', '44620', '44621', '44629', '4463', '4464', '4465', '4466', '4467',
                                                  '4470', '4471', '4472', '4473', '4474', '4475', '4476', '44770', '44771', '44772', '44773', '4478', '4479', '4480',
                                                  '4481', '4489', '449']),1,0)
# --> Peripheral Vascular Disease (AFRI)
cabg_ind['pvd'] = np.where(cabg_ind['d_ICD'].isin(['44020', '44021', '44022', '44023', '44024', '44029', '4430', '4431', '44321', '44322', '44323', '44324', '44329', 
                                                   '44381', '44389', '4439', '45981', '74760', '74769', '9972']),1,0)
# --> Left Atrial Dilation (NPOAF)
cabg_ind['lad'] = np.where(cabg_ind['d_ICD'].isin(['4293']),1,0)
# --> Mild Mitral Valve Disease (NPOAF)
cabg_ind['mild'] = np.where((cabg_ind['notes'].str.contains('mild mitral')),1,0)
cabg_ind['mvd'] = np.where((cabg_ind['d_ICD'].isin(['3940', '3941', '3942', '3949', '3960', '3961', '3962', '3963', '3968', '3969'])),1,0)
mask_1_m = ((cabg_ind['mild'].astype(str) == "1") & (cabg_ind['mvd'].astype(str) == "1"))
mask_0_m = ((cabg_ind['mild'].astype(str) == "0") & (cabg_ind['mvd'].astype(str) == "1")) | (cabg_ind['mvd'].astype(str) == "0")
cabg_ind.loc[mask_0_m, 'mmvd'] = 0
cabg_ind.loc[mask_1_m, 'mmvd'] = 1
# --> Moderate to Severe Mitral Valve Disease (NPOAF)
mask_1_s = ((cabg_ind['mild'].astype(str) == "0") & (cabg_ind['mvd'].astype(str) == "1"))
mask_0_s = ((cabg_ind['mild'].astype(str) == "1") & (cabg_ind['mvd'].astype(str) == "1")) | (cabg_ind['mvd'].astype(str) == "0")
cabg_ind.loc[mask_0_s, 'smvd'] = 0
cabg_ind.loc[mask_1_s, 'smvd'] = 1
# --> COPD (POAF)
cabg_ind['copd'] = np.where(cabg_ind['d_ICD'].isin(['49320', '49321', '49322']),1,0)
# --> Intra-aortic Balloon Pump (POAF)
cabg_ind['iabp'] = np.where(cabg_ind['p_ICD'].isin(['3596']),1,0)
# --> Combined Valve/Artery Surgery (POAF)
cabg_ind['cvas'] = np.where(cabg_ind['p_ICD'].isin(['3500', '3501', '3502', '3503', '3504', '3505', '3506', '3507', '3509', '3510', '3511', '3512', '3513', '3514',
                                                   '3520', '3521', '3522', '3523', '3524', '3525', '3526', '3527', '3528', '3539', '3599']),1,0)
# --> Emergency (POAF)
cabg_ind['emergency'] = np.where(cabg_ind['type']=='EMERGENCY',1,0)
# --> Dialysis (POAF)
cabg_ind['dialysis'] = np.where(cabg_ind['p_ICD'].isin(['3895','3995','5498']),1,0)
# --> myocardial infaction (Simplified)
cabg_ind['MI'] = np.where((cabg_ind['d_ICD'].isin(['41000', '41001', '41002', '41010', '41011', '41012', '41020', '41021', '41022', '41030', '41031', '41032', '41040', '41041', '41042', '41050', '41051', '41052', '41060', '41061','41062','41070','41071','41072','41080','41081','41082','41090','41091','41092'])),1,0)
# --> Atrial Fibrillation (outcome for all risk scores)
cabg_ind['AF'] = np.where((cabg_ind['d_ICD']=='42731'),1,0)

### Aggregate indicators for each subject and admission
indicators = cabg_ind.drop(columns=['d_ICD',
                                    'p_ICD',
                                    'type',
                                    'mild',
                                    'mvd'
                           ]).groupby(['subject_id','hadm_id'], as_index=False).max()


## Risk Score Calculation
### Establish a function to calculate POAF(Cameron et al., 2018)
def poaf(x):
    poaf=0
    if (60 <= x['age'] <= 69):
        poaf=poaf+1
    if (70 <= x['age'] <= 79): 
        poaf=poaf+2
    if (x['age'] >= 80):
        poaf=poaf+3
    if (x['copd'] == 1):
        poaf=poaf+1
    if (x['eGFR'] < 15):
        poaf=poaf+1
    elif (x['dialysis'] == 1):
        poaf=poaf+1
    if (x['emergency'] == 1):
        poaf=poaf+1
    if (x['iabp'] == 1):
        poaf=poaf+1
    if (x['cvas'] == 1):
        poaf=poaf+1
    return poaf

### Establish a function to calculate CHADS2 (Cameron et al., 2018)
def chads2(x):
    chads2=0
    if (x['chf'] == 1):
        chads2=chads2+1
    if (x['hbp'] == 1):
        chads2=chads2+1
    if (x['age'] >= 75):
        chads2=chads2+2
    if (x['dm'] == 1):
        chads2=chads2+1
    if (x['stroke'] == 1):
        chads2=chads2+2
    if (x['pvd'] == 1):
        chads2=chads2+1
    if (65 <= x['age'] <= 74):
        chads2=chads2+1
    if (x['gender'] == 'F'):
        chads2=chads2+1
    return chads2

### Establish a function to calculate AFRI (Cameron et al., 2018)
def afri(x):
    afri=0
    if (x['gender'] == 'M'):
        if (x['age'] > 60):
            afri=afri+1
        if (x['weight'] > 76):
            afri=afri+1
        if (x['height'] > 176):
            afri=afri+1
        if (x['pvd'] == 1):
            afri=afri+1
    elif (x['gender'] == 'F'):
        if (x['age'] > 66):
            afri=afri+1
        if (x['weight'] > 64):
            afri=afri+1
        if (x['height'] > 168):
            afri=afri+1
        if (x['pvd'] == 1):
            afri=afri+1
    return afri

### Establish a function to calculate NPOAF (Tran et al., 2015)
def npoaf(x):
    npoaf=0
    if (65 <= x['age'] <= 74):
        npoaf=npoaf+2
    if (x['age'] >= 75):
        npoaf=npoaf+3
    if (x['mmvd'] == 1):
        npoaf=npoaf+1
    if (x['smvd'] == 1):
        npoaf=npoaf+3
    if (x['lad'] == 1):
        npoaf=npoaf+1
    return npoaf

### Establish a function to calculate Simplified POAF (Chen et al., 2018)
def simplified(x):
    simplified=0
    if (x['age'] >= 65):
        simplified=simplified+2
    if (x['hbp'] == 1):
        simplified=simplified+2
    if (x['MI'] == 1):
        simplified=simplified+1
    if (x['chf'] == 1):
        simplified=simplified+2
    return simplified

### Establish a function to calculate COM-AF (Burgos et al., 2021)
def comaf(x):
    comaf=0
    if (65 <= x['age'] <= 74):
        comaf=comaf+1
    if (x['age'] >= 65):
        comaf=comaf+2
    if (x['gender'] == 'F'):
        comaf=comaf+1
    if (x['hbp'] == 1):
        comaf=comaf+1
    if (x['dm'] == 1):
        comaf=comaf+1
    if (x['stroke'] == 1):
        comaf=comaf+2
    return comaf

### Apply the functions to calculate the risk scores
indicators['poaf'] = indicators.apply(poaf, axis=1)
indicators['chads2'] = indicators.apply(chads2, axis=1)
indicators['afri'] = indicators.apply(afri, axis=1)
indicators['npoaf'] = indicators.apply(npoaf, axis=1)
indicators['simplified'] = indicators.apply(simplified, axis=1)
indicators['comaf'] = indicators.apply(comaf, axis=1)

### Export the final dataset for use in the dashboard
indicators.to_csv('../../Data/risk.csv')