# Rebellio

服务器

python version == 3.6.9

pip3 install django
pip3 install pymysql
pip3 install django-simple-captcha

python manage.py makemigrations
python manage.py migrate --fake-initial

# Rbdx看板页面功能设计

## 1. 谱面相关页面

### 1.1 谱面商店

用户根据自己的custom point购买谱面，custom point根据游玩记录获得，谱面购买后在自己的商店页面出现

### 1.2 谱面一览

查看发布的所有谱面，可以直接下载rb文件
支持喜欢和收藏功能
收藏的谱面可以单独查看
可以根据热度、发布时间、名称、谱面作者、曲名、音源作者进行谱面检索
支持导航到对应曲包
支持评论功能，可以通过评论导航到用户主页

### 1.3 曲包一览

查看所有曲包，可以根据名字、发布时间、谱面名字进行检索
支持导航到对应谱面

### 1.4 内测谱面功能

登录后内测权限用户享有
可以上传谱面，上传后所有内测用户都能在商店看到该谱面

## 2. 个人信息页面

登录功能

### 2.1 个人页面主页

展示自己的custom point(根据游玩成绩计算)，等级(游玩数量决定），个性签名，头像和用户名以及最近10个游玩曲目和成绩

展示段位(生成个性化的段位认证图)

根据用户设置是否对其他成员可见

### 2.2 个人页面游玩历史

个人页面最近游玩: 展示全部游玩历史，分页，默认按照时间排序

谱面成绩记录: 所有谱面的成绩记录，记录游玩次数，最高成绩，最近成绩。支持按照等级天梯图排序或按照名字排序(默认)

### 2.3 好友功能

添加好友，从好友列表点进个人主页

搜索玩家，点进个人主页

## 3. 段位系统

考段位，在页面发起开始后在页面显示的指定时间内完成下一首歌的游玩，如果不按照指定顺序或时间内游玩，则直接判定为失败

成功后根据用户头像生成一份定制段位认证图，在用户首页展示

## 4. 统计功能

内测权限用户可查看

根据歌曲的喜欢，游玩次数统计得到歌曲热度，展示月度/周度歌曲热度信息

# 资料

https://www.jianshu.com/p/36c44fb04d4a
https://www.cnblogs.com/derek1184405959/p/8567522.html
https://zhuanlan.zhihu.com/p/138678484
https://segmentfault.com/a/1190000006110417
https://waxdoll.gitbooks.io/webdesignfoundations/content/appendix/font_browser_default.html
https://code.z01.com/v4/components/card.html