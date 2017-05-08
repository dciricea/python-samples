# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 13:49:40 2015

@author: diana

Covers:

- Waiting for other processes/Patients
- Resources: Doctors

Scenario:
  A hospital has a limited number of doctors and defines
  a treatment processes that takes some (random) time.

  Patient arrives at the hospital at a random time. If one doctor
  is available, they start the treatment process and wait for it
  to finish. If not, they wait until a doctor is available.
"""

import random
import simpy
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RANDOM_SEED = 100
NUM_DOCTORS = int(input('How many doctors in the hospital: ')) # Number of doctors in the hospital
INIT_PATIENTS = int(input('How many initial patients in the hospital: ')) # Number of initial patients in the hospital
TREAT_TIME = 30      # Minutes it takes to treat a patient, aprox 30 minutes +/-15 mins
PATIENT_INTER = 15   # Create a new patient that comes to the hospital every 15 minutes, +/- 5 mins
SIM_TIME = 24*60     # Simulation time in minutes


data = []  # This list of touples will hold all collected data

patients_simtime_in_hospital = [] #list of touples tracks time and patients in hopital at that time

busy_doctors = [] #list that tracks wich doctor is availbale to treat a patient, since simpy is not providing this

all_doctors = range(1, NUM_DOCTORS+1) #list that keeps all doctors

patients_in_hospital = 0

#generates random priority
def genPriority():
    return random.randint(1,10)
    
# Generates reandom treatment time. The higher the patient priority (1..10),1 is the highest, 10 the lowest priority
# it should take longer to treat the problem    
def getTreatmentTime(patientPriority):
    return int((1/patientPriority) * 10 * random.randint(TREAT_TIME-15, TREAT_TIME+15))   
  
#simpy recsouce allocation function used to track program output  
def print_resstats(res):
     print(' %d of %d doctors are allocated, waiting patients %d.' % (res.count, res.capacity, len(res.queue)))
     #print('  Users:', len(res.users), '  Queued events:', len(res.queue))
  
#function that returns doctors available    
def getMinDoctorAvailable():
    #print (busy_doctors)
    return min(set(all_doctors) - set(busy_doctors))
    #simpy doesn't have priority for the resources so I assign  first the doctor that is repesented by the lowest number

#Simulates patients    
def patient(env, name, priority, hospital):
    #Tracks patients in hopital at this moment
    global patients_in_hospital
    """This generator function models the patient process (each patient has a ``name``) arrives at the hospital
     and requests a doctor to see him. Once the doctor is available, it then starts the treatment process, 
     waits for it to finish and leaves """
    arrival_time = env.now
    print('%s with priority %d checked in at minute %d' % (name, priority, arrival_time))
    patients_in_hospital = patients_in_hospital + 1
    patients_simtime_in_hospital.append((arrival_time, patients_in_hospital))
    
    #request based on patient priority, TODO check preempt=True
    #SimPy documentation to request a resource
    with hospital.doctors.request(priority) as request:
        #print_resstats(hospital.doctors)
        #wait until a doctor is available for this patient
        yield request

        #I got the doctor, tell me which one
        doc = getMinDoctorAvailable()
        print('Doctor %d available, %s is seen by doctor at minute %d.' % (doc, name, env.now))
        busy_doctors.append(doc)
        waiting_time = env.now - arrival_time
        
        #simulate the treatment to keep the doctor busy
        yield env.process(hospital.treat(name, priority))

        print('%s discharged at minute %d.' % (name, env.now))
        
        busy_doctors.remove(doc)
        #patient left the hospital
        patients_in_hospital = patients_in_hospital -1
        patients_simtime_in_hospital.append((env.now, patients_in_hospital))
        
        print_resstats(hospital.doctors)
        
        #add info to my statistics list
        data.append((name, priority, arrival_time, env.now, waiting_time, doc));
#print(data)

class Hospital(object):
    """A Hospital has a limited number of doctors (``NUM_DOCTORS``) to
    work on patients in parallel.
    Patients have to request one of the shared resources, doctors. When they got one, they
    can start the treatment processes and wait for it to finish (which
    takes ``TREAT_TIME`` minutes).
    """
    
    def __init__(self, env):
        self.env = env
        #priority queue
        self.doctors = simpy.PriorityResource(env, NUM_DOCTORS)
        
        #preemptive test
        #self.doctors = simpy.PreemptiveResource(env, NUM_DOCTORS)
        

    def treat(self, patient, patientPriority):
        """The treatment processes. It takes a ``patient`` processes and tries
        to talk to him and solve his problem."""
        patient_treat_time = getTreatmentTime(patientPriority) 
        yield self.env.timeout(patient_treat_time)

        print("%s with priority %d was treated in %d minutes." % (patient, patientPriority, patient_treat_time))
        #print_resstats(self.doctors)
        
def setup(env):
    """Create a hospital, a number of initial patients and keep creating patients
    approx. every ``PATIENT_INTER`` minutes."""
    # Create the hospital
    hospital = Hospital(env)

    print("%d initial Patients waiting to be seen" % INIT_PATIENTS)
    init_patients=[]    
    
    print_resstats(hospital.doctors)
    
    #generating priorities for initial patients
    for i in range(1, INIT_PATIENTS+1):
        init_patients.append(('Patient %3d' % i, genPriority()))

    for (patient_name, patient_priority) in sortInitial(init_patients):  
        #add a patient to queue waiting for doctors
        env.process(patient(env, patient_name, patient_priority, hospital))
        
    # Create more patients while the simulation is running
    while True:
        #print("Current sim time", env.now)
        create_patient_time = random.randint(PATIENT_INTER-5, PATIENT_INTER+5)
        #print("New patient will be comming in %d minutes" % create_patient_time)
        yield env.timeout(create_patient_time)
        i += 1
        #Send it to the hospital front desk
        env.process(patient(env, 'Patient %3d' % i, genPriority(), hospital))

#sort a touple by first item  (Patient Number, PatientPrioeity)
def getPatientPriority(patientData):
    return patientData[1]

#Sort patients by patient priority
def sortInitial(patients):
    return sorted(patients, key=getPatientPriority)

#Prints all data about a patient visit
def print_patient_stats():
    for (patient, priority, in_time, out_time, wait_time, doc) in data:
        print('%s priority %2d, arrived at %4d, discharged after %d minutes, waiting %d minutes, treated by Doctor %d' % (patient, priority, in_time, (out_time - in_time), wait_time, doc))


#Makes 3 plots
def plot_data():
    
    #prepare ploting data
    doc_pat = {}
    pat_prio = {}
    waiting_times = []
    for (patient, priority, in_time, out_time, wait_time, doc) in data:
        waiting_times.append(wait_time)
        if (not doc in doc_pat.keys()):
            doc_pat[doc] = 1
        else:
            doc_pat[doc] = doc_pat[doc]+1
        
        if (not priority in pat_prio.keys()):
            pat_prio[priority] = 1
        else:
            pat_prio[priority] = pat_prio[priority]+1    
    
    #Plots how many patient each doctor treated during the simulation time
    x = list(doc_pat.keys())
    y = list(doc_pat.values())
    plt.xlabel("Doctor name")
    plt.ylabel("Number of patients seen")
    #colors=np.random.rand(NUM_DOCTORS)
    plt.bar(x,y)
    plt.show()
    
    #Ploting what percent of patient with priority were treated
    x = list(pat_prio.keys())
    y = list(pat_prio.values())
    plt.xlabel("Percent of patients with priority")
    from matplotlib import cm
    cs=cm.Set1(np.arange(10)/10.)
    plt.pie(y, labels=x, autopct='%1.1f%%', shadow=True, colors=cs)
    plt.show()
    
    # Plot of waiting time per patient
    plt.xlabel("Patient number")
    plt.ylabel("Patient waiting time in minutes")
    plt.plot(range(1, len(waiting_times) +1), waiting_times)
    plt.show()
   
    # Patient in the hospital in time
    simtime = [ pair[0] for pair in patients_simtime_in_hospital]
    patients_in_hospital = [ pair[1] for pair in patients_simtime_in_hospital]
    plt.xlabel("Simulation time in minutes")
    plt.ylabel("Patients in hopital")
    plt.plot(simtime, patients_in_hospital)
    plt.show()

#function that write the data to a csv file
def write_to_csv():
    file_name = 'stats.csv'
    with open(file_name, 'w') as csvfile:
        fieldnames = ['patient', 'priority', 
                      'in_time', 'out_time', 'wait_time', 
                      'treat_time', 'doctor']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
        writer.writeheader()
        for (patient, priority, in_time, out_time, wait_time, doctor) in data:
            writer.writerow({'patient':patient, 'priority':priority, 
                             'in_time':in_time, 'out_time':out_time, 
                             'wait_time':wait_time, 
                             'treat_time':(out_time - in_time - wait_time),
                             'doctor': doctor})
    print("Data was saved to file ", file_name)
 
    
# Setup and start the simulation
print('ER simulation started')

# This helps reproducing the results on multiple runs
random.seed(RANDOM_SEED)  

# Create an environment and start the setup process
env = simpy.Environment()
env.process(setup(env))

# Execute the process, main body
env.run(until=SIM_TIME)

print('Hospital simulation completed.')

#print_patient_stats()

plot_data()

write_to_csv()

mydata = pd.read_csv('./stats.csv')
cols = list(mydata.columns.values)
#print(cols)

for i in range(1,11):
    print(mydata[mydata['priority']==i])
  

#print (patients_simtime_in_hospital)