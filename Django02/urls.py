"""
URL configuration for Django02 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path

from django.contrib import admin
from django.urls import path,include,reverse

from . import views,testdb,search,search2


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.runoob),
    path('testdb/', testdb.testdb),
    path('testdb1/', testdb.testdb1),
    path('testdb2/', testdb.testdb2),
    path('testdb3/', testdb.testdb3),
    path('testdb4/', testdb.testdb4),
    path('hello/', views.runoob),
    path('index/',views.index),
    path('search-form/', search.search_form),
    path('search/', search.search1),
    path('search-post/', search2.search_post),
    path("TestModel/", include("TestModel.urls")),
    path("app01/", include("app01.urls")),
    path("cookie/", include("cookie.urls")),
    path('v1/', include('blog.urls')),
    path('api-auth/', include('rest_framework.urls')),

#    path("login1/", views.login, name="login"),
#    re_path(r"^login/(?P<year>[0-9]{4})/$", views.login2, name="login2")
    path("login/", views.Login.as_view()),


]



