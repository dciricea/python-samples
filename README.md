# python-samples
Python code samples

### hospital.py
The application simulates an emergency room environment with a given number of doctors that treat patients in the order of their arrival and priority. Patients are coming at a set interval with random variation and randomly assigned priority from 1-10 (where 1 has the highest priority). The patients are put in a queue waiting to be seen by the next available physician. The simulation output data is recorded for plotting and exporting in a csv file for the purpose of future reporting, resource tracking and analysis.

### Continuous Renal Replacement Therapy Data Analysis and predictive modeling crrt.ipynb
The dataset used in this study was extracted from the latest version of the MIMIC data, MIMIC-III. The data was loaded in Postgresql relational database for better visualization and faster processing. 
Out if the 12691 total number of ICU admission with a diagnosis of ARF I was able to extract 1686 ICU admission for which there was recorded that the hemodialysis procedure was performed. These were unique ICU admission that had a combination of ARF diagnosis and hemodialysis procedure.

The majority of the data analysis and model construction was done in Python using Anaconda distribution. The main libraries used were Pandas and Sklearn for machine learning.

The final data set used was exported from Postgresql in the form of a csv analytic file and loaded in Python Jupiter notebook using pandas library. The pandas library converted the csv file into a DataFrame structure for further preprocessing and analysis. The csv file imported had missing values for the laboratory values not recorded. In this step I filled in the missing values with the mean value, as sklearn can’t handle missing values. Once the unnecessary attributes were removed, the data set was split into 80% for training and 20% for testing. Several machine learning methods (Random Forest, Logistic Regression, GaussianNB, SVM) were applied and the results ploted.


### form_cgiScript.py
Basic script to run on a webserver to simulate a web form 


