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
    path('fumen/unlocked_fumens/', views.get_unlocked_fumens),
    path('fumen/own_fumens/', views.get_own_fumens),
    path('fumen/fumen_detail/', views.get_fumen),
    path('fumen/create_fumen_comment/', views.create_fumen_comment),
    path('fumen/update_fumen_comment/', views.update_fumen_comment),
    path('fumen/delete_fumen_comment/', views.delete_fumen_comment),
    # 曲包
    path('pack/packs/', views.get_packs),
    path('pack/pack_detail/', views.get_pack),
    path('pack/create_pack_comment/', views.create_pack_comment),
    path('pack/update_pack_comment/', views.update_pack_comment),
    path('pack/delete_pack_comment/', views.delete_pack_comment),
    # 玩家
    path('user/user_search/', views.user_search),
    path('user/user_detail/', views.get_user_detail),
    path('user/get_available_avatar/', views.get_available_avatar),
    path('user/set_avatar/', views.set_avatar),
    path('user/user_info_set/', views.user_info_set),
    path('user/set_user_info/', views.set_user_info),
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
    path('inner/view_fumen_comment', views.view_fumen_comment),
    url(r'^captcha', include('captcha.urls')),
    #path('fumen/get', views.get_fumen),
]
