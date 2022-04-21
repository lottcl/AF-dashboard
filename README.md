# Atrial Fibrillation Clinical Dashboard

This documentation allows the user to deploy an interactive clinical dashboard for calculating atrial fibrillation risk scores. The app must be deployed on your local machine, and it can be run using the command line or by running the code in the Jupyter notebooks. The repository does not include the sample data, but all data was obtained from MIT's MIMIC-III dataset and the MIMIC-Extract output files. Data should be placed in the corresponding data folders within the repository.

## File set-up

To install from the source:

    $ git clone git@github.com:lottcl/AF_dashboard.git
    $ cd AF_dashboard
    $ python setup.py develop

### Using [MIMIC-III](https://mimic.mit.edu/docs/iii/) as the reference dataset

You will need to acquire credentialed access to MIMIC through [physionet](https://mimic.physionet.org/gettingstarted/cloud/). Once you are a credentialed user, you can access the data through the cloud or through file downloads. You will need to add the following tables to AF-Dashboard/Data/MIMIC-III:

    * ADMISSIONS
    * DIAGNOSES_ICD
    * NOTEEVENTS
    * PATIENTS
    * PROCEDURES_ICD

You will also need to add the MIMIC-Extract output H5 data file to AF-Dashboard/Data/MIMIC-Extract. The [MIMIC-Extract GitHub repository](https://github.com/MLforHealth/MIMIC_Extract) provides instructions for how to obtain cloud access to the output datsaet or conduct the data processing steps using the code provided.

## Command Line Instructions

To run the processing code:

    $ cd AF_dashboard/Code/Python_files
    $ Python AF_process.py
    $ Rscript Code/Python_files/imp_creatinine.R
    $ Python AF_process_post_impute.py

To run deploy the dashboard:

    $ cd AF_dashboard/Code/Python_files
    $ Python AF_dashboard.py


## JupyterLab instructions

To run the processing code and deploy the dashboard on JupyterLab, you will need to install the following packages using conda or pip:

    * pandas
    * numpy
    * datetime
    * dash >= 1.20
    * dash_bootstrap_components
    * dash_bootstrap_templates
    * waitress
    * plotly
    * statsmodels

To install JupyterDash, follow the instructions in the [Jupyter Dash documentation](https://github.com/plotly/jupyter-dash)

<br> **Note: JupyterLab functionality is still under development for this project so Command Line is the recommended method for deploying the dashboard**
