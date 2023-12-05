from django.shortcuts import render, redirect
from django.urls import path,include,reverse
from django.http import HttpResponse
from django.views import View
import pdb;
def runoob(request):
    context = {}
    context['hello'] = '***     Hello World!   ****'
    views_list1 = ["a", "b", "c", "d", "e"]
    views_list2 = []
    views_name = "菜鸟教程"
    views_list = ["菜鸟教程1", "菜鸟教程2", "菜鸟教程3"]
    views_dict = {"name":"菜鸟教程","age":18}
    name = "菜鸟教程"
    num = 1024
    import datetime
    now = datetime.datetime.now()
    views_str = "<a href='https://www.runoob.com/'>点击跳转</a>"
    views_num = 88
    #return render(request, "runoob.html", {"num": views_num})
    #return render(request, "runoob.html", {"views_str": views_str})
    #return render(request, "runoob.html", {"time": now})
    #return render(request, "runoob.html", {"num": num})
    #return render(request, "runoob.html", {"name": context})
    #return render(request, "runoob.html", {"views_dict": views_dict})
    #return render(request, "runoob.html", {"views_list": views_list})
    #return render(request, "runoob.html", {"name1": views_name})
    #return render(request, 'runoob.html', context)
    #return render(request, "../templates/runoob.html", {"listvar": views_list1})
    return render(request, "runoob.html", {"name": name})


def login1(request):
    ctx = {}
    if request.method == "GET":
        message ='This is GET Request'
    elif request.method == "POST":
        message = 'This is POST Request'
    else:
        message = "Unknow Request"

    ctx['message'] = message

    if request.method == "GET":
        #return HttpResponse("菜鸟教程"+message)
        return render(request, "Route.html", {"rlt": ctx})
    else:
        username = request.POST.get("username")
        pwd = request.POST.get("pwd")
        if username == "菜鸟教程" and pwd =="菜鸟教程" :
            return HttpResponse("菜鸟教程 "+message)
        else:
            return redirect(reverse("login"))


def login2(request,year):
    ctx = {}
    if request.method == "GET":
        message ='This is GET Request'
    elif request.method == "POST":
        message = 'This is POST Request'
    else:
        message = "Unknow Request"

    ctx['message'] = message

    if request.method == "GET":
        #return HttpResponse("菜鸟教程"+message)
        return render(request, "Route2.html", {"rlt": ctx})
    else:
        username = request.POST.get("username")
        pwd = request.POST.get("pwd")
        if username == "菜鸟教程" and pwd =="菜鸟教程" :
            return HttpResponse("菜鸟教程 "+message)
        else:
            return redirect(reverse("login2",kwargs={"year":3333}))


def index(Request):
    print("index视图")
    return redirect("/hello/")
    #return HttpResponse("OKKK")

class Login(View):
    def get(self,request):
        print("GET 方法")
        return render(request, "login.html")


    def post(self,request):
        user = request.POST.get("username")
        pwd = request.POST.get("pwd")
        if user == "Francis" and pwd == "999":
            return HttpResponse("POST 方法1")
        else:
            return HttpResponse("POST 方法 2")

