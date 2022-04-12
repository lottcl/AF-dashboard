# Atrial Fibrillation Clinical Dashboard

This documentation allows the user to deploy an interactive clinical dashboard for calculating atrial fibrillation risk scores. The app must be deployed on your local machine, and it can be run using the command line or by running the code in the Jupyter notebooks. The repository does not include the sample data, but all data was obtained from MIT's MIMIC-III dataset and the MIMIC-Extract output files. Data should be placed in the corresponding data folders within the repository.

## Command-line set-up

To install from the source:

$ git clone git@github.com:lottcl/AF_dashboard.git
$ cd cvdm
$ python setup.py develop


To run the processing code and deploy the dashboard:

$ make dashboard


## JupyterLab set-up

To run the processing code and deploy the dashboard on JupyterLab, you will need to install the following packages using conda or pip:

    * pandas
    * numpy
    * datetime
    * sqlite3
    * jupyter_dash
    * dash
    * dash_bootstrap_components
    * plotly
    * kaleido
    * dash_bootstrap_templates
    * statsmodels

To install JupyterDash, follow the instructions in the [Jupyter Dash documentation](https://github.com/plotly/jupyter-dash)
