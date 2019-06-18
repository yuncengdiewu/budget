简介
----
利用python语句写的基于网络爬虫的预算系统，其中static为静态文件存放的位置，列如以.js、.css和照片等的文件；ACMbudget为整个大项目中的配置文件，最重要的是setting配置文件和urls文件；budget为整个项目的核心文件，含源代码文件以及templates中的.html文件

Mysql
-------
首先安装Mysql，本系统以Mysql作为数据库，建立budg数据库

pycharm
----------
安装pycharm后，导入文件。设置虚拟环境，安装django，用pip安装PyMySQL

数据库配置和运行
-----------
在pycharm下运行命令：python manage.py makemigrations和python manage.py migrate 进行数据迁移（向MySQL中建表）

在pycharm下运行命令：python manage.py createsuperuser 建立超级管理员（邮箱可为空）

运行项目，点击运行结果中的链接，在链接后面添加/admin，登录，进入Django管理员界面，在Admi中创建第一个用户（用户类型为总教练）

点击运行结果中的链接，使用之前创建的用户登录系统即可
