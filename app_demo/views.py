from django.shortcuts import render
from django.shortcuts import redirect
import pymysql
from django.template.defaultfilters import escape


db = pymysql.connect("localhost", "root", "12345678", "Bug_Report")
#db=pymysql.connect("localhost", "root", "root", "Bug_Report")


def login(request):
    if request.session.get('is_login', None):
        return redirect('/index')
    if request.method == "GET":
        return render(request, 'login/login.html')
    if request.method=="POST" and "button_register" in request.POST:
        return render(request, 'login/login.html', locals())
    else:
        username = request.POST['username']
        password = request.POST['password']
        message = "user name or password can't be empty"
        if username.strip() and password:
            sql = "SELECT uid,pswd FROM `user` WHERE dname=%s"
            cursor = db.cursor()
            cursor.execute(sql, [username])
            result = cursor.fetchone()
            if result is None:
                message = "No such user"
                return render(request, 'login/login.html', locals())
            else:
                #when result is null
                #uid, pswd = result report error
                uid, pswd = result
                if pswd == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = uid
                    request.session['user_name'] = username
                    return redirect('/index/')
                else:
                    message = 'wrong password'
                    return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/login.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    request.session.flush()
    return redirect("/login/")

def register(request):
    if request.method == "POST" and "button_register" not in request.POST and "button_back" not in request.POST:
        return render(request, 'login/register.html')
    if request.method=="POST" and "button_register" in request.POST:
        sql="insert into `user`(dname,email,uname,pswd) values(%s,%s,%s,%s)"
        cursor=db.cursor()
        cursor.execute(sql,[request.POST.get('dname'),request.POST.get('email'),request.POST.get('nickname'),request.POST.get('password')])
        db.commit()
        return redirect("/login/")
    if request.method=="POST" and "button_back" in request.POST:
        return redirect("/login/")




def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    sql = "SELECT * FROM project"
    cursor = db.cursor()
    cursor.execute(sql, [])
    result = cursor.fetchall()
    return render(request, 'login/index.html', {'record_list': result})



def newproject(request):
    if request.method=='POST' and 'button_submit' in request.POST:
        project_title = escape(request.POST.get('project_title'))
        project_dscpt = escape(request.POST.get('project_des'))
        sql="insert into project(pname,uid,pdscpt) values(%s,%s,%s)"
        cursor = db.cursor()
        cursor.execute(sql,[project_title, request.session['user_id'],project_dscpt])
        sql="select wid,wname from workflow"
        cursor.execute(sql,[])
        available_workflow=cursor.fetchall()
        db.commit()
        sql="select pid from project where pname=%s"
        cursor.execute(sql,project_title)
        newprojectId = cursor.fetchone()
        request.session['newprojectId'] =newprojectId
        sql = "insert into flowrelationship values(%s,1,5)"
        cursor.execute(sql, newprojectId)
        sql= "insert into `lead` values(%s,%s)"
        cursor.execute(sql,[newprojectId,request.session['user_id']])
        db.commit()
        sql="select wid,next_wid from flowrelationship where pid=%s"
        cursor.execute(sql,newprojectId)
        current_workflow=cursor.fetchall()
        return render(request, 'login/newproject.html', {'available_workflow': available_workflow,'current_workflow':current_workflow})
    if request.method == 'POST' and 'button1' in request.POST:
        newprojectId=request.session['newprojectId']
        sql = "select wid,wname from workflow"
        cursor = db.cursor()
        cursor.execute(sql, [])
        available_workflow = cursor.fetchall()
        sql = "insert into flowrelationship values(%s,%s,%s)"
        p_w = escape(request.POST.get('previousWorkflow'))
        n_w = escape(request.POST.get('next_Workflow'))
        cursor.execute(sql,[newprojectId,p_w,n_w])
        db.commit()
        sql = "select wid,next_wid from flowrelationship where pid=%s"
        cursor.execute(sql, newprojectId)
        current_workflow = cursor.fetchall()
        return render(request, 'login/newproject.html', {'available_workflow': available_workflow, 'current_workflow': current_workflow})
    if request.method=='POST' and 'button2' in request.POST:
        newprojectId=request.session['newprojectId']
        sql="insert into workflow(wname) values(%s)"
        cursor = db.cursor()
        n_w = escape(request.POST.get('new_workflow'))
        cursor.execute(sql, n_w)
        db.commit()
        sql = "select wid,wname from workflow"
        cursor.execute(sql, [])
        available_workflow = cursor.fetchall()
        sql = "select wid,next_wid from flowrelationship where pid=%s"
        cursor.execute(sql, newprojectId)
        current_workflow = cursor.fetchall()
        return render(request,'login/newproject.html', {'available_workflow': available_workflow, 'current_workflow': current_workflow})



def projectdetail(request):
    if request.method == 'GET':
        pid = request.GET.get('pid')
        request.session['pid'] = pid
        sql = "SELECT iid,dname,title,idscpt,wname,ctime FROM issue NATURAL JOIN workflow NATURAL JOIN user WHERE pid = %s"
        cursor = db.cursor()
        cursor.execute(sql, [pid])
        result = cursor.fetchall()
        return render(request, 'login/projectdetail.html', {'issue_list': result})
    if request.method == 'POST' and 'button1' in request.POST:
        pid=request.session['pid']
        sql="insert into issue(uid,pid,title,idscpt,wid,ctime) values(%s,%s,%s,%s,1,NOW())"
        cursor=db.cursor()
        new_issue_title=request.POST['title']
        new_issue_describe=escape(request.POST.get('describe',False))
        pid = request.session['pid']
        cursor.execute(sql,[request.session['user_id'],pid,new_issue_title,new_issue_describe])
        db.commit()
        sql = "SELECT iid,dname,title,idscpt,wname,ctime FROM issue NATURAL JOIN workflow NATURAL JOIN user WHERE pid = %s"
        cursor = db.cursor()
        cursor.execute(sql, [pid])
        result = cursor.fetchall()
        return render(request, 'login/projectdetail.html', {'issue_list': result})
    if request.method == 'POST' and 'button2' in request.POST:
        search_title = escape(request.POST.get('search_title', False))
        pid = request.session['pid']
        sql_title = "SELECT iid, dname, title, idscpt, wname,ctime FROM issue NATURAL JOIN USER NATURAL JOIN workflow WHERE pid=%s and title like %s"
        cursor = db.cursor()
        cursor.execute(sql_title, [pid, "%"+search_title+"%"])
        issues = cursor.fetchall()
        return render(request, 'login/projectdetail.html', {'issue_list': issues})
    if request.method == 'POST' and 'button3' in request.POST:
        search_user = escape(request.POST.get('search_name', False))
        pid = request.session['pid']
        sql_title = "SELECT iid, dname, title, idscpt, wname,ctime FROM issue NATURAL JOIN USER NATURAL JOIN workflow WHERE pid=%s and dname like %s"
        cursor = db.cursor()
        cursor.execute(sql_title, [pid, "%"+search_user+"%"])
        issues = cursor.fetchall()
        return render(request, 'login/projectdetail.html', {'issue_list': issues})
    if request.method == 'POST' and 'button4' in request.POST:
        time = escape(request.POST.get('Time scope', False))
        pid = request.session['pid']
        sql_filter_time = "SELECT iid, dname, title, idscpt, wname,ctime FROM issue NATURAL JOIN USER NATURAL JOIN workflow WHERE pid=%s and DATE_SUB(NOW(), INTERVAL %s hour)< ctime"
        cursor = db.cursor()
        cursor.execute(sql_filter_time, [pid, time])
        issues = cursor.fetchall()
        return render(request, 'login/projectdetail.html', {'issue_list': issues})


def issuedetail(request):
    global global_iid
    issues = []
    if request.method == 'GET':
        iid = request.GET.get('iid')
        global_iid=iid
    if request.method=='POST' and 'button1' in request.POST:
        iid=global_iid
        new_title=request.POST['title']
        new_descr=escape(request.POST.get('IssueDescr',False))
        updatesql="update issue set title=%s,idscpt=%s where iid=%s"
        cursor=db.cursor()
        cursor.execute(updatesql,[new_title,new_descr,iid])
        db.commit()
    if request.method=='POST' and 'button2' in request.POST:
        iid = global_iid
        new_wid = escape(request.POST.get('next_status', False))
        cursor = db.cursor()
        cursor.execute("SELECT pid,wid FROM issue WHERE iid=%s", [iid])
        result = cursor.fetchone()
        pid = result[0]
        old_wid = result[1]
        uid = request.session['user_id']
        sql_updatehistory = "INSERT INTO history(iid,pid,updatedate,old_wid,new_wid,uid) values (%s,%s,NOW(),%s,%s,%s)"
        cursor.execute(sql_updatehistory, [iid, pid, old_wid, new_wid, uid])
        db.commit()
        sql_updateissue = "UPDATE issue set wid=%s where iid=%s"
        cursor.execute(sql_updateissue, [new_wid, iid])
        db.commit()
    sql = "select iid,pid,updatedate,new_wname,dname,wname from (select iid,pid,updatedate,wname as new_wname,old_wid,uid from history join workflow on new_wid=wid) as B join workflow on old_wid=wid natural join user where iid = %s"
    cursor = db.cursor()
    cursor.execute(sql, [iid])
    result = cursor.fetchall()
    sql1="SELECT pid from issue where iid=%s"
    cursor.execute(sql1,[iid])
    pid=cursor.fetchone()
    sql2="SELECT iid,dname,title,idscpt,wname,ctime FROM issue NATURAL JOIN workflow NATURAL JOIN user WHERE pid = %s and iid=%s"
    cursor.execute(sql2, [pid,iid])
    result1 = cursor.fetchone()
    sql_getwid = "SELECT wid FROM issue WHERE iid=%s"
    cursor.execute(sql_getwid, [iid])
    curr_status = cursor.fetchone()[0]
    sql_getnextstatus = "SELECT next_wid FROM flowrelationship WHERE wid=%s"
    cursor.execute(sql_getnextstatus, [curr_status])
    nextstatus = cursor.fetchall()
    status_list = "("
    for status in nextstatus:
        status_list += str(status[0]) + ","
    status_list = status_list[:-1] + ")"
    sql_getnextstatusname = "SELECT wid,wname FROM workflow WHERE wid in" + status_list
    cursor.execute(sql_getnextstatusname, [])
    statusname = cursor.fetchall()
    uid = request.session["user_id"]
    sql = "SELECT iid FROM assignment WHERE uid=%s"
    cursor.execute(sql, uid)
    iid_list = cursor.fetchall()
    print(iid_list)
    if (int(global_iid),) in iid_list:
        return render(request, 'login/issuedetail.html', {'issue_history':result, 'issue_current':result1, 'issue_nextstatus':statusname,})
    else:
        return render(request, 'login/issuedetail.html', {'issue_history':result, 'issue_current':result1, 'issue_nextstatus':statusname, 'permission':[False]})


def myproject(request):
    if request.method == 'GET':
        uid = request.GET.get('uid')
        print(uid)
        sql = "SELECT `lead`.pid,pname,pdscpt FROM `lead` JOIN project on `lead`.pid = project.pid  WHERE `lead`.uid=%s"
        cursor = db.cursor()
        cursor.execute(sql, [int(uid)])
        my_project_list = cursor.fetchall()
        return render(request, 'login/myproject.html', {'my_project_list': my_project_list})
    if request.method == 'POST' and 'assign' in request.POST:
        pid = escape(request.POST.get('project_id', False))
        uid = escape(request.POST.get('user_id', False))
        sql_add_lead = "INSERT INTO `lead`(pid, uid) VALUES (%s, %s)"
        cursor = db.cursor()
        cursor.execute(sql_add_lead, [int(pid), int(uid)])
        db.commit()
        uid = request.session["user_id"]
        sql="SELECT pid,pname,pdscpt FROM project WHERE uid=%s"
        cursor = db.cursor()
        cursor.execute(sql, [uid])
        my_project_list = cursor.fetchall()
        return render(request, 'login/myproject.html', {'my_project_list': my_project_list})

def myissue(request):
    if request.method == 'GET':
        pid = escape(request.GET.get('pid'))
        request.session['pid'] = pid
        sql = "SELECT iid,dname,title,idscpt,wname,ctime FROM issue NATURAL JOIN workflow NATURAL JOIN user WHERE pid = %s"
        cursor = db.cursor()
        cursor.execute(sql, [pid])
        result = cursor.fetchall()
        return render(request, 'login/myissue.html', {'issue_list': result})
    if request.method == 'POST' and 'assign' in request.POST:
        iid = escape(request.POST.get('issue_id', False))
        uid = escape(request.POST.get('user_id', False))
        pid = request.session['pid']
        sql_add_lead = "INSERT INTO assignment(iid, uid, pid) VALUES (%s, %s, %s)"
        cursor = db.cursor()
        cursor.execute(sql_add_lead, [int(iid), int(uid), pid])
        db.commit()
        sql = "SELECT iid,dname,title,idscpt,wname,ctime FROM issue NATURAL JOIN workflow NATURAL JOIN user WHERE pid = %s"
        cursor = db.cursor()
        cursor.execute(sql, [pid])
        result = cursor.fetchall()
        return render(request, 'login/myissue.html', {'issue_list': result})


def myassignment(request):
    if request.method == 'GET':
        uid = request.session["user_id"]
        sql = "SELECT iid,dname,title,idscpt,wname,ctime FROM issue NATURAL JOIN workflow NATURAL JOIN user NATURAL JOIN assignment WHERE uid = %s"
        cursor = db.cursor()
        cursor.execute(sql, [uid])
        my_issue_list = cursor.fetchall()
        return render(request, 'login/myassignment.html', {'my_issue_list': my_issue_list})
