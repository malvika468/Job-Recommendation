import csv
import sys
csv.field_size_limit(sys.maxsize)
from pprint import pprint
import numpy as np
import pickle

jobdetails = pickle.load(open('C:\Users\user\Desktop\CF\project\jobdetails.p',"rb"))
appdetails = pickle.load(open('C:\Users\user\Desktop\CF\project\Appdetails.p',"rb"))
user_to_index = pickle.load(open('C:\Users\user\Desktop\CF\project\user_to_index.p',"rb"))
job_to_index = pickle.load(open('C:\Users\user\Desktop\CF\project\job_to_index.p',"rb"))

users = len(user_to_index)
jobs = len(job_to_index)

print users,jobs

#matrix = [[0 for ii in range(jobs)] for jj in range(users)]

for key in user_to_index.keys(): 
    userindex = user_to_index[key]
    hisjobs = appdetails[key]
    print hisjobs
    for job in hisjobs:
        jobindex=job_to_index[job]
        #matrix[userindex][jobindex]=1
            
       
"""		
np.save('matrix',matrix)	 		
m=np.load('matrix.npy')
m=np.array(m)
print m.shape 
"""
























