from flask import Flask, flash, redirect, render_template, request, session, abort
import item_item
 
app = Flask(__name__)
 
@app.route("/")
def index():
    return render_template('index.html')
 
@app.route("/registered_user")
def registered_user():
    return render_template('registered_user.html',msg="")

@app.route("/login",methods=['POST'])
def login():
	userid = int(request.form['userid'])
	pwd = request.form['pwd']
	print "Userid:",userid
	print "pwd:",pwd
	if userid < 0 or userid > 7900 or pwd != "pass" :
		print "Wrong UserID or Password."
		return render_template('registered_user.html',msg="Wrong UserID or Password")
	else:
		print "Correct UserID."
		appliedjobs,finaljobs = item_item.getRecJobsWeb(userid)
		#appliedjobs,finaljobs = item_item.kmeans_rec(userid)
		print "appliedjobs = ",appliedjobs
		print "finaljobs = ",finaljobs
		return render_template('dashboard.html',userid=userid,recjobs=finaljobs,appjobs=appliedjobs,msg="")
	return render_template('registered_user.html',msg="Some Error.")

@app.route("/apply",methods=['POST'])
def apply():
	userid = int(request.form['userid'])
	jobid = request.form['jobid']
	try:
		appliedjobs,finaljobs = item_item.apply(userid,jobid)
		return render_template('dashboard.html',userid=userid,recjobs=finaljobs,appjobs=appliedjobs,msg="Successfully Applied for Job.")
	except :
		return render_template('registered_user.html',msg="Some Error Ocuurred. Login Again.")

@app.route("/logout")
def logout():
    return render_template('registered_user.html',msg="")
 
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)