#load the mice package
library(mice)
library(here)

#set identify the location of the project
i_am("Code/Processing/imp_creatinine.R")

#read in the data
na_creatinine <- read.csv(here("Data/MIMIC-III/na_creatinine.csv"))

#run the auto-imputation using the mice package
imp_creatinine <- complete(mice(na_creatinine))

#export the data to use for score calculation
write.csv(imp_creatinine, here("Data/MIMIC-III/imp_creatinine.csv"))
