from django.shortcuts import render, redirect
from django.views.decorators import csrf
from django.http import HttpResponse

# 接收POST请求数据
def search_post(request):
    ctx = {}
    if request.method == "GET":
        message ='This is GET Request'
    elif request.method == "POST":
        message = 'This is POST Request'
    else:
        message = "Unknow Request"

    if request.method == 'POST':
        ctx['rlt'] = request.POST['q']
        name = request.path
        print(name)
        #return redirect("/hello/")
        #return HttpResponse("<a href='https://www.runoob.com/'>菜鸟教程11</a>" + message)


    ctx['message'] = message

    return render(request, "post.html", {"rlt":ctx})