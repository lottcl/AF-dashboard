dashboard: Code/Python_files/AF_dashboard.py Data/risk.csv
	Python Code/Python_files/AF_dashboard.py

Data/risk.csv: Code/Python_files/AF_process_post_impute.py Data/MIMIC-III/imp_creatinine.csv Data/MIMIC-III/DIAGNOSES_ICD.csv.gz Data/MIMIC-III/NOTEEVENTS.csv.gz ../../Data/MIMIC-III/PROCEDURES_ICD.csv.gz Data/MIMIC-III/ADMISSIONS.csv.gz
	Python Code/Python_files/AF_process_post_impute.py

Data/MIMIC-III/imp_creatinine.csv: Code/Python_files/imp_creatinine.R Data/MIMIC-III/na_creatinine.csv
	Rscript Code/Python_files/imp_creatinine.R

Data/MIMIC-III/na_creatinine.csv: Code/Python_files/AF_process.py Data/MIMIC-III/PROCEDURES_ICD.csv.gz Data/MIMIC-Extract/all_hourly_data.h5 Data/MIMIC-III/ADMISSIONS.csv.gz Data/MIMIC-III/PATIENTS.csv.gz
	Python Code/Python_files/AF_process.py

.PHONY: dashboard