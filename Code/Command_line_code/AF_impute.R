#install and load mice and here packages
if(!require("mice"))(install.packages("mice"))
library("mice")
if(!require("here"))(install.packages("here"))
library("here")

#set identify the location of the project
i_am("Code/Processing/Command_line_code/AF_impute.R")

#read in the data
na_creatinine <- read.csv(here("Data/MIMIC-III/na_creatinine.csv"))

#run the auto-imputation using the mice package
imp_creatinine <- complete(mice(na_creatinine))

#export the data to use for score calculation
write.csv(imp_creatinine, here("Data/MIMIC-III/imp_creatinine.csv"))
