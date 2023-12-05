from django.http import HttpResponse
from django.shortcuts import render


# 表单
def search_form(request):
    if request.method == "GET":
        message='This is GET Request'
    elif request.method == "POST":
        message = 'This is POST Request'
    else:
        message = "Unknow Request"
    return render(request, 'search_form.html',{"message": message})



def search(request):
    message = '错误的调用'
    return HttpResponse(message)

# 接收请求数据
def search1(request):
    if request.method == "GET":
        message='This is GET Request'
    elif request.method == "POST":
        message = 'This is GET Request'
    else:
        message = "Unknow Request"

    request.encoding = 'utf-8'
    if 'wq' in request.GET and request.GET['wq']:
        message1 = message +'你搜索的内容为: ' + request.GET['wq']
    else:
        message1 = message+'你提交了空表单'

    return HttpResponse(message1)