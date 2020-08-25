"""Rebellio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url
from django.conf.urls import include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', views.test),
    path('login/', views.login),
    path('logout/', views.logout),
    path('home/', views.home),
    path('fumen/', views.get_fumens),
    path('fumen/own_fumen/', views.get_own_fumens),
    path('fumen/fumen_detail/', views.get_fumen),
    path('fumen/comment_on_fumen/', views.comment_on_fumen),
    url(r'^captcha', include('captcha.urls')),
    #path('fumen/get', views.get_fumen),
]
