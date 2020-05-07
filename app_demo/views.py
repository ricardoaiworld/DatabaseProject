from django.shortcuts import render
from django.shortcuts import redirect
import pymysql
from django.http import HttpResponse


#db = pymysql.connect("localhost", "root", "12345678", "Bug_Report")
db=pymysql.connect("localhost", "root", "root", "Bug_Report")


def login(request):
    if request.session.get('is_login', None):
        return redirect('/index')
    if request.method == "GET":
        return render(request, 'login/login.html')
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


def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    sql = "SELECT * FROM project"
    cursor = db.cursor()
    cursor.execute(sql, [])
    result = cursor.fetchall()
    return render(request, 'login/index.html', {'record_list': result})


def projectdetail(request):
    if request.method == 'GET':
        pid = request.GET.get('pid')
        sql = "SELECT iid,dname,title,idscpt,wname,ctime FROM issue NATURAL JOIN workflow NATURAL JOIN user WHERE pid = %s"
        cursor = db.cursor()
        cursor.execute(sql, [pid])
        result = cursor.fetchall()
    return render(request, 'login/projectdetail.html', {'issue_list': result})

def issuedetail(request):
    if request.method == 'GET':
        iid = request.GET.get('iid')
        sql = "select iid,pid,updatedate,new_wname,dname,wname from (select iid,pid,updatedate,wname as new_wname,old_wid,uid from history join workflow on new_wid=wid) as B join workflow on old_wid=wid natural join user where iid = %s"
        cursor = db.cursor()
        cursor.execute(sql, [iid])
        result = cursor.fetchall()

        sql1="SELECT pid from history where iid=%s"
        cursor.execute(sql1,[iid])
        pid=cursor.fetchone()
        sql2="SELECT iid,dname,title,idscpt,wname,ctime FROM issue NATURAL JOIN workflow NATURAL JOIN user WHERE pid = %s and iid=%s"
        cursor.execute(sql2, [pid,iid])
        result1 = cursor.fetchone()
    return render(request, 'login/issuedetail.html', {'issue_history':result, 'issue_current':result1})

