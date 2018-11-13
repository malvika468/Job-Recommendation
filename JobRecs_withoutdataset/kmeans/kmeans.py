# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 22:11:52 2017

@author: nisha
"""

import numpy as np
from scipy.sparse.linalg import svds
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_error
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import pickle
from sklearn.cluster import KMeans
from collections import defaultdict
from scipy.spatial.distance import euclidean
import operator
from collections import Counter

"""
jobdetails = pickle.load(open('C:\Users\\nisha\Desktop\CF\Project\jobdetails.p',"rb"))
job_to_index = pickle.load(open('C:\Users\\nisha\Desktop\CF\project\job_to_index.p',"rb"))
job_Cat_to_index = pickle.load(open('C:\Users\\nisha\Desktop\CF\project\job_Cat_to_index.p',"rb"))
print len(jobdetails) , len(job_Cat_to_index)
jobs=len(jobdetails)
cat=145
Job_matrix=np.zeros((jobs,cat))
for key in jobdetails.keys():
    jobindex=job_to_index[key]
    category=jobdetails[key]
    for cat in category:
        cat_ind=job_Cat_to_index[cat]
        Job_matrix[jobindex][cat_ind]=1

np.save('Job_matrix',Job_matrix)
print "saved"   
"""


def rank(recJobs,most_freq_clust,Job_matrix,total_app):
    cost={}
    final_rec=[]
    for job in recJobs:
        dist=np.linalg.norm(centroids[most_freq_clust]-Job_matrix[job])
        cost[job]=dist
    c=0    
    for key , value in sorted(cost.items(),key=operator.itemgetter(1)):
        c+=1
        final_rec.append(key)
        if(c==total_app):
            break
    return final_rec
            

Job_matrix=np.load('Job_matrix.npy')
kmeans = KMeans(n_clusters=200, random_state=0).fit(Job_matrix)
centroids=kmeans.cluster_centers_
cluster_to_job=defaultdict(list)
job_to_cluster={}

for i in range(len(Job_matrix)):
    C=kmeans.predict(Job_matrix[i].reshape(1,-1))
    c=C[0]
    job_to_cluster[i]=c
    cluster_to_job[c].append(i)
        
#print len(cluster_to_job) , len(job_to_cluster) , 
matrix=np.load('matrix.npy')
for uid in range(matrix.shape[0]):
    uid=24
    hisjobs=np.where(matrix[uid] == 1)[0]
    total_app = len(hisjobs)
    clust=[]
    for job in hisjobs:
        l=job_to_cluster[job]
        clust.append(l)    
    most_freq_clust=max(set(clust),key=clust.count)
    recm_jobs=cluster_to_job[most_freq_clust]
    #top=rank(recm_jobs,most_freq_clust,Job_matrix,total_app)
    appset=set(hisjobs)
    recset=set(recm_jobs)
    common=appset.intersection(recset)
    print len(common)
    
    print "precision" ,len(common)/float(len(recm_jobs))
    print "recall" ,len(common)/float(len(hisjobs))
    
    """
    X=TSNE(n_components=2).fit_transform(Job_matrix,labels)
    plt.scatter(X[:,0],X[:,1],c=labels,cmap=plt.cm.cool,s=4)
    """



     
        
            