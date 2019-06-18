"""ACMbudget URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from budget import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name='login'),
    path('index/userinfo', views.showuser, name='userinfo'),
    path('creuserajax', views.ajax_cre_user, name='ajax_cre_user'),
    path('deuserajax', views.ajax_de_user, name='ajax_de_user'),
    path('upuserajax', views.ajax_up_user, name='ajax_up_user'),
    path('ajax_se_user', views.ajax_se_user, name='ajax_se_user'),
    path('index', views.creindex, name='creindex'),
    path('ajax_up_own', views.ajax_up_own, name='ajax_up_own'),
    path('unlogin', views.unlogin, name='unlogin'),

    path('index/cjys', views.el_list, name='eltail'),
    path('index/getcitylist_provinceID<int:provinceID>', views.city_list),
    path('index/create', views.cre, name='cre'),
    path('index/<int:e_id>', views.showele, name='selel'),
    path('selel2', views.selel2, name='selel2'),
    path('ajax_up_ele', views.ajax_up_ele, name='ajax_up_ele'),
    path('ajax_de_ele', views.ajax_de_ele, name='ajax_de_ele'),

    path('index/zzjs', views.ul_list, name='ul_list'),
    path('index/zzys/<int:u_id>', views.showult, name='showult'),
    path('index/zzys/cre<int:e_id>', views.cre_ult, name='cre_ult'),
    path('ajax_cre_ult', views.ajax_cre_ult, name='ajax_cre_ult'),
    path('ajax_up_ult', views.ajax_up_ult, name='ajax_up_ult'),
    path('ajax_de_ult',views.ajax_de_ult, name='ajax_de_ult'),
    path('ajax_se_ult', views.ajax_se_ult, name='ajax_se_ult'),

    path('index/sjzd', views.account_list, name='account_list'),
    path('index/sjzd/cre<int:u_id>', views.cre_account, name='cre_account'),
    path('ajax_cre_account', views.ajax_cre_account, name='ajax_cre_account'),
    path('index/sjzd/<int:acco_id>', views.show_account, name='show_account'),
    path('ajax_up_account', views.ajax_up_account, name='ajax_up_account'),
    path('ajax_de_account', views.ajax_de_account, name='ajax_de_account'),
    path('ajax_se_account', views.ajax_se_account, name='ajax_se_account'),
    path('index/sjzd/year<int:year>', views.accountyear, name='accountyear'),

    path('insdex/qt<int:type>', views.show_qt, name='show_qt'),
    path('ajax_se_qt', views.ajax_se_qt, name='ajax_se_qt'),
    path('ajax_cre_qt', views.ajax_cre_qt, name='ajax_cre_qt'),
    path('ajax_de_qt', views.ajax_de_qt, name='ajax_de_qt'),
]
