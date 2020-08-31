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
    # 主要页面
    path('home/', views.home),
    path('login/', views.login),
    path('logout/', views.logout),
    # 谱面
    path('fumen/fumens/', views.get_fumens),
    path('fumen/unlocked_fumen/', views.get_unlocked_fumens),
    path('fumen/own_fumen/', views.get_own_fumens),
    path('fumen/fumen_detail/', views.get_fumen),
    path('fumen/comment_on_fumen/', views.comment_on_fumen),
    path('fumen/delete_comment/', views.delete_comment),
    # 曲包
    path('pack/packs/', views.get_packs),
    path('pack/pack_detail/', views.get_pack),
    path('pack/comment_on_pack/', views.comment_on_pack),
    # 内部
    path('inner/home/', views.inner_home),
    path('inner/subdiff_votes/', views.get_subdiff_votes),
    path('inner/vote_on_subdiff/', views.vote_on_subdiff),
    path('inner/advice_fumens/', views.get_advice_fumens),
    path('inner/update_packs/', views.update_packs),
    path('inner/update_subdiffs/', views.update_subdiffs),
    path('inner/add_subdiff_vote_fumen/', views.add_subdiff_vote_fumen),
    path('inner/delete_subdiff_vote_fumen/', views.delete_subdiff_vote_fumen),
    path('inner/super_manager/', views.super_manager),
    path('inner/change_user_access_level', views.change_user_access_level),
    url(r'^captcha', include('captcha.urls')),
    #path('fumen/get', views.get_fumen),
]
