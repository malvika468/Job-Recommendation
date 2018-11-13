import numpy as np
from pprint import pprint
import math
from scipy import spatial
import pickle
import h5py
from operator import itemgetter
from sklearn.cluster import KMeans
from collections import defaultdict

def average(x):
    return float(sum(x)) / len(x)

def pearson_def(x, y):
    n = len(x)
    if n == 0:
        return -1
    avg_x = average(x)
    avg_y = average(y)
    diffprod = 0
    xdiff2 = 0
    ydiff2 = 0
    for idx in range(n):
        xdiff = x[idx] - avg_x
        ydiff = y[idx] - avg_y
        diffprod += xdiff * ydiff
        xdiff2 += xdiff * xdiff
        ydiff2 += ydiff * ydiff
    if xdiff2 == 0 or ydiff2 == 0: # Correlation undefined, here we take it as -1
        return -1
    return diffprod / math.sqrt(xdiff2 * ydiff2)

def cosine_similarity(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    if sumxx*sumyy == 0:
        return 0
    return sumxy/math.sqrt(sumxx*sumyy)



matrix = np.load("./dataset/matrix/matrix.npy")
# pprint(matrix)
print "Matrix shape:",matrix.shape

# users,jobs = matrix.shape[0],matrix.shape[1]
# cal_sim = False


def getSimUser(userid,matrix):
	sims = []
	find_user = matrix[userid]	
	for user in range(matrix.shape[0]):
		#print "Progress=>",user
		other_user = matrix[user]
		#curr_sim = cosine_similarity(find_user,other_user)
		curr_sim = 1 - spatial.distance.cosine(find_user, other_user)
		sims.append(curr_sim)
	topusers = sorted(range(len(sims)), key=lambda k: sims[k],reverse=True)
	return topusers[:12]

def rankjobs(jobs):
	result = []
	for entry in set(jobs):
	    result.append((entry, jobs.count(entry)))
	result.sort(key = lambda x: -x[1])
	return result

def apply(userid,jobid):
	job_to_index = pickle.load(open("./index/job_to_index.p","rb"))
	jobind = job_to_index[jobid]
	matrix[userid][jobind] = 1
	return getRecJobsWeb(userid)

def getRecJobsWeb(userid):

	#matrix = np.load("./dataset/matrix/matrix.npy")

	#h5f = h5py.File('./dataset/matrix/matrix.h5','r')
	#matrix = h5f['matrix'][:]
	#h5f.close()
	
	## loading the jobs information
	jobs = pickle.load(open("./dataset/jobs.dict","rb"))


	simusers = getSimUser(userid,matrix)#[1, 682, 7628, 3424, 2088, 4250, 1003, 1238, 7009, 84, 4658, 7907] # 
	recjobs = []
	for uu in simusers:
		for jj in range(len(matrix[0])):
			if matrix[userid][jj] == 0 and matrix[uu][jj] == 1:
				recjobs.append(jj)
	#print "All jobs : ",len(recjobs)
	#print "Unique jobs : ",len(set(recjobs))
	topjobs = rankjobs(recjobs)[:30]
	#print "Ranked Jobs : ",topjobs
	finaljobs = []
	for j in topjobs:
		finaljobs.append(j[0])
	print "finaljobs:",finaljobs
	appliedjobs = np.where(matrix[userid] == 1)[0] 

	## loading the index to job index 
	index_to_job = pickle.load(open("./index/index_to_job.p","rb"))

	originalapp = [index_to_job[key] for key in appliedjobs]
	originalrec = [index_to_job[key] for key in finaljobs]

	appinfo,recinfo = [],[]
	for appid in originalapp:
		try:
			appinfo.append([appid]+[jobs[appid][0].decode('utf-8')]+jobs[appid][1:])
		except KeyError:
			print "JOBID NOT FOUND : ",appid
	for recid in originalrec:
		try:
			recinfo.append([recid]+jobs[recid])
		except KeyError:
			print "JOBID NOT FOUND : ",recid

	### Sort first 10 recommended jobs according to salary and vacancies
	### For experienced people, salary is important. For others, vacancies is important.
	appinfo_np,recinfo_np = np.array(appinfo),np.array(recinfo)
	rec10 = list(recinfo[:10])

	## get estimate of experience of the user from his/her applied jobs
	exp = appinfo_np[:,7]
	print "exp:",exp
	exp_list = []
	for e in exp:
		try:
			exp_list.append(int(e.replace(" ","")[0]))
		except ValueError:
			pass
	#exp_list = [int(e.replace(" ","")[0]) for e in exp]
	#print "exp_list:",exp_list
	max_exp = max(exp_list)
	print "rec10:",rec10

	if max_exp > 5: ## if bigger experience then sort it according to maximum salary, then by vacancies
		#rec10 =  sorted(rec10,key=itemgetter(5,6),reverse=True)
		rec10 = sorted(rec10, key=lambda x: (-x[5], -x[6]))
	else:           ## vice versa otherwise
		#rec10 = sorted(rec10,key=itemgetter(6,5),reverse=True)
		rec10 = sorted(rec10, key=lambda x: (-x[6], -x[5]))
	print "Len(rec10):",len(rec10)
	print "Len(recinfo):",len(recinfo)

	return appinfo,rec10 + recinfo[10:] #originalapp,originalrec #appliedjobs,finaljobs

def kmeans_rec(uid):

	#h5f = h5py.File('./dataset/matrix/matrix.h5','r')
	#matrix = h5f['matrix'][:]
	#h5f.close()
	matrix = np.load("./dataset/matrix/matrix.npy")
	print "Matrix loaded."
	
	## loading the jobs information
	jobs = pickle.load(open("./dataset/jobs.dict","rb"))

	Job_matrix=np.load('./dataset/matrix/Job_matrix.npy')
	#kmeans = KMeans(n_clusters=20, random_state=0).fit(Job_matrix)

	## saving the model
	#pickle.dump(kmeans,open("./dataset/matrix/kmeans.model","wb"))

	# loading the model
	kmeans = pickle.load(open("./dataset/matrix/kmeans.model","rb"))

	centroids=kmeans.cluster_centers_
	cluster_to_job=defaultdict(list)
	job_to_cluster={}

	for i in range(len(Job_matrix)):
		C=kmeans.predict(Job_matrix[i].reshape(1,-1))
		c=C[0]
		job_to_cluster[i]=c
		cluster_to_job[c].append(i)
	        
	#print len(cluster_to_job) , len(job_to_cluster) , 
	#matrix=np.load('matrix.npy')
	# for uid in range(matrix.shape[0]):
	#     uid=24
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
	#common=appset.intersection(recset)
	#print len(common)

	#print "precision" ,len(common)/float(len(recm_jobs))
	#print "recall" ,len(common)/float(len(hisjobs))

	appliedjobs,finaljobs= list(appset),list(recset)[:30]
	print "Applied jobs= ",appliedjobs
	print "Rec jobs= ",finaljobs

	## loading the index to job index 
	index_to_job = pickle.load(open("./index/index_to_job.p","rb"))

	originalapp = [index_to_job[key] for key in appliedjobs]
	originalrec = [index_to_job[key] for key in finaljobs]

	appinfo,recinfo = [],[]
	for appid in originalapp:
		try:
			appinfo.append([appid]+jobs[appid])
		except KeyError:
			print "JOBID NOT FOUND : ",appid
	for recid in originalrec:
		try:
			recinfo.append([recid]+jobs[recid])
		except KeyError:
			print "JOBID NOT FOUND : ",recid

	### Sort first 10 recommended jobs according to salary and vacancies
	### For experienced people, salary is important. For others, vacancies is important.
	appinfo_np,recinfo_np = np.array(appinfo),np.array(recinfo)
	rec10 = list(recinfo[:10])

	## get estimate of experience of the user from his/her applied jobs
	exp = appinfo_np[:,7]
	#print "exp:",exp
	exp_list = []
	for e in exp:
		try:
			exp_list.append(int(e.replace(" ","")[0]))
		except ValueError:
			pass
	#exp_list = [int(e.replace(" ","")[0]) for e in exp]
	#print "exp_list:",exp_list
	max_exp = max(exp_list)
	#print "rec10:",rec10

	if max_exp > 5: ## if bigger experience then sort it according to maximum salary, then by vacancies
		#rec10 =  sorted(rec10,key=itemgetter(5,6),reverse=True)
		rec10 = sorted(rec10, key=lambda x: (-x[5], -x[6]))
	else:           ## vice versa otherwise
		#rec10 = sorted(rec10,key=itemgetter(6,5),reverse=True)
		rec10 = sorted(rec10, key=lambda x: (-x[6], -x[5]))
	print "Len(rec10):",len(rec10)
	print "Len(recinfo):",len(recinfo)

	return appinfo,rec10 + recinfo[10:] #originalapp,originalrec #appliedjobs,finaljobs

def getRecJobs(userid,matrix):

	simusers = getSimUser(userid,matrix)#[1, 682, 7628, 3424, 2088, 4250, 1003, 1238, 7009, 84, 4658, 7907] # 
	recjobs = []
	for uu in simusers:
		for jj in range(len(matrix[0])):
			if matrix[userid][jj] == 0 and matrix[uu][jj] == 1:
				recjobs.append(jj)
	#print "All jobs : ",len(recjobs)
	#print "Unique jobs : ",len(set(recjobs))
	topjobs = rankjobs(recjobs)[:100]
	#print "Ranked Jobs : ",topjobs
	finaljobs = []
	for j in topjobs:
		finaljobs.append(j[0])
	print finaljobs
	return finaljobs

def getRecJobsPrecision(userid,matrix):

	simusers = getSimUser(userid,matrix)#[1, 682, 7628, 3424, 2088, 4250, 1003, 1238, 7009, 84, 4658, 7907] # 
	recjobs = []
	for uu in simusers:
		for jj in range(len(matrix[0])):
			if matrix[uu][jj] == 1:
				recjobs.append(jj)
	#print "All jobs : ",len(recjobs)
	#print "Unique jobs : ",len(set(recjobs))
	topjobs = rankjobs(recjobs)[:30]
	#print "Ranked Jobs : ",topjobs
	finaljobs = []
	for j in topjobs:
		finaljobs.append(j[0])
	print finaljobs
	appliedjobs = np.where(matrix[userid] == 1)[0] 
	return appliedjobs,finaljobs

#getSimUser(1,matrix)
#getRecJobs(1000,matrix)

### Testing ####
# making the entries 0 in the matrix


# def testingdata(matrix):
# 	testing_entries = []
# 	for uid in range(matrix.shape[0]):
# 		#jobid = list(matrix[uid]).index(1) ## getting the first job
# 		jobids = np.where(matrix[uid] == 1)[0] ## getting applied jobids
# 		testing_entries.append((uid,jobids[5]))
# 		testing_entries.append((uid,jobids[10]))
# 		testing_entries.append((uid,jobids[15]))
# 		testing_entries.append((uid,jobids[20]))
# 		testing_entries.append((uid,jobids[25]))
# 		matrix[uid][jobids[5]] = 0 ## changing the value to 0
# 		matrix[uid][jobids[10]] = 0 ## changing the value to 0
# 		matrix[uid][jobids[15]] = 0 ## changing the value to 0
# 		matrix[uid][jobids[20]] = 0 ## changing the value to 0
# 		matrix[uid][jobids[25]] = 0 ## changing the value to 0
# 		#break
# 	return matrix,testing_entries


# def evaluate(matrix,testing_entries):
# 	correct = 0
# 	total = 0
# 	for ent in testing_entries:
# 		total += 1
# 		uid = ent[0]
# 		jobid = ent[1]
# 		finaljobs = getRecJobs(uid,matrix)
# 		print "Applied Jobids: ",jobid
# 		print "Recommended Jobs: ",finaljobs
# 		if jobid in finaljobs :
# 			correct += 1
# 			print "Correct Recommendation"
# 		print "Accuracy : ",float(correct)/total
# 		#break

# matrix,testing_entries = testingdata(matrix)
# evaluate(matrix,testing_entries)


def calPrecision(userid):
	applied,rec=getRecJobsPrecision(userid,matrix)
	appset = set(applied)
	recset = set(rec)
	common = appset.intersection(recset)
	print "common=",common
	precision = float(len(common))/len(recset)
	print "Precision : ",precision
	recall = float(len(common))/len(appset)
	print "Recall : ",recall
	return precision,recall

# totalprec,totalrec = 0,0
# for u in range(100):
# 	p,r = calPrecision(u)
# 	totalprec += p
# 	totalrec += r
# print "Average precision = ",float(totalprec)/100
# print "Average recall = ",float(totalrec)/100

#app,rec = getRecJobsWeb(15)
#pprint(rec)

#app,rec = kmeans_rec(9)
#pprint(rec)