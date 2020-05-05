from django.shortcuts import render
from django.shortcuts import redirect
import pymysql
from django.http import HttpResponse


db = pymysql.connect("localhost", "root", "12345678", "Bug_Report")
cursor = db.cursor()


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
            cursor.execute(sql, [username])
            result = cursor.fetchone()
            uid, pswd = result
            if result is None:
                message = "No such user"
                return render(request, 'login/login.html', locals())
            else:
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
    return render(request, 'login/index.html')
    '''
    sql = "SELECT pname, pdscpt FROM project WHERE uid = %s"
    cursor.execute(sql, [])
    result = cursor.fetchall()
    print(result)
    '''
    return render(request, 'login/index.html')
