import json
from datetime import datetime, timedelta

from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from .models import Eleb, Admi, STra, ETra, SAir, EAir, Acc, CName, LoginAdmi, Ultb, Account
from .forms import LoginForm, CreForm
from django.db.models import F, Q
from django.db.models import Max, Avg, F, Q, Min, Count, Sum
from .tra import creTra
from .air import creAir
from .hotel import ceAcc

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)

def login(request):
    if request.method == 'POST':
        userform = LoginForm(request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']
            try:
                user = Admi.objects.get(name=username, password=password)
                LoginAdmi.objects.all().delete()
                us = LoginAdmi.objects.create(user=user)
                us.save()
                cnam = CName.objects.all()
                return render_to_response('index.html', {'user': user, 'cnam': cnam})
            except:
                userform = LoginForm()
                return render_to_response('login.html', {'userform': userform, 'pass_error': True})
    else:
        userform = LoginForm()
    return render_to_response('login.html', {'userform': userform, 'pass_error': False})
def creindex(request):
    user = LoginAdmi.objects.all()[0].user
    if user:
        cnam = CName.objects.all()
        return render_to_response('index.html', {'user': user, 'cnam': cnam})
    else:
        return render_to_response('login.html')
def showuser(request):
    users = LoginAdmi.objects.all()
    user = users[0].user
    userinfo = Admi.objects.all()
    return render_to_response('userinfo.html', {'userinfo': userinfo, 'user': user})
def ajax_cre_user(request):
    if request.is_ajax():
        username = request.POST['username']
        data = {'if_succes': True}
        try:
            User_error = Admi.objects.get(name=username)
            data['if_succes'] = False
            data = json.dumps(data)
            return HttpResponse(data)
        except:
            password = request.POST['password']
            ty = request.POST['ty']
            nu = Admi.objects.create(name=username, password=password, ty=ty)
            nu.save()
            data = json.dumps(data)
            return HttpResponse(data)
def ajax_de_user(request):
    if request.is_ajax():
        de_idlist = request.POST.getlist('de_idlist')
        user_id = LoginAdmi.objects.all()[0].user.pk
        user_id = str(user_id)
        data = {'de_succes': True}
        for de_id in de_idlist:
            if (de_id == user_id):
                data['de_succes'] = False
            else:
                try:
                    Admi.objects.get(pk=de_id).delete()
                except:
                    data['de_succes'] = False
        data = json.dumps(data)
        return HttpResponse(data)
def ajax_up_user(request):
    if request.is_ajax():
        tp = request.POST['tp']
        oldele = request.POST['oldele']
        newele = request.POST['newele']
        if tp == '1':
            Admi.objects.filter(name=oldele).update(name=newele)
        elif tp == '2':
            Admi.objects.filter(name=oldele).update(password=newele)
        else:
            if newele == '总教练':
                Admi.objects.filter(name=oldele).update(ty=True)
            else:
                Admi.objects.filter(name=oldele).update(ty=False)
        data = json.dumps({'tp': tp})
        return HttpResponse(data)
def ajax_se_user(request):
    if request.is_ajax():
        username = request.POST['username']
        users = LoginAdmi.objects.all()
        user = users[0].user
        userinfo = Admi.objects.get(name=username)
        dd = {'use_pk': userinfo.pk, 'user_ty': user.ty, 'username': userinfo.name, 'usepas': userinfo.password,
              'usty': userinfo.ty}
        data = json.dumps(dd)
        return HttpResponse(data)
def ajax_up_own(request):
    if request.is_ajax():
        user_id = LoginAdmi.objects.all()[0].user.pk
        password = request.POST['password']
        Admi.objects.filter(pk=user_id).update(password=password)
        data = json.dumps({'up_succes': True})
        return HttpResponse(data)
def unlogin(request):
    LoginAdmi.objects.all().delete()
    return render_to_response('unlog.html')

def se_traion(tratp, st, et, site):
    st1 = st - timedelta(days=1)
    et1 = et + timedelta(days=1)
    if tratp:
        strtraion = STra.objects.filter(etime__gte=st1, site=site).filter(etime__lte=st, site=site)
        endtraion = ETra.objects.filter(stime__gte=et, site=site).filter(stime__lte=et1, site=site)
    else:
        strtraion = SAir.objects.filter(etime__gte=st1, site=site).filter(etime__lte=st, site=site)
        endtraion = EAir.objects.filter(stime__gte=et, site=site).filter(stime__lte=et1, site=site)
    return (strtraion, endtraion)
def el_list(request):
    elelist = Eleb.objects.all()
    years = []
    for ele in elelist:
        if ele.name[:4] not in years:
            years.append(ele.name[:4])
    sorted(years);
    return render_to_response('cjys.html', {'elelist': elelist, 'years': years})
def jiaotong1(stime, etime, site):
    (strtraion, endtraion) = se_traion(True, stime, etime, site)
    (strair, endair) = se_traion(False, stime, etime, site)
    train = {}
    pr = 0
    for tra in strtraion:
        if (pr < tra.price):
            train['st_train'] = tra
            pr = tra.price
    pr = 0
    for tra in endtraion:
        if (pr < tra.price):
            train['end_train'] = tra
            pr = tra.price
    pr = 0
    for air in strair:
        if (pr < air.price):
            train['st_air'] = air
            pr = air.price
    pr = 0
    for air in endair:
        if (pr < air.price):
            train['end_air'] = air
            pr = air.price
    return train
def city_list(request, provinceID):
    with open('static/json/city.json', 'rb') as f:
        citys = json.load(f)
    i = 1
    j = 1
    cit = ''
    for ci in citys.keys():
        if (i == provinceID):
            cit = ci
            break
        j += len(citys[ci])
        i += 1
    citys = citys[cit]
    cit_list = {'star': j, 'end': j + len(citys)}
    return HttpResponse(json.dumps(cit_list))
def pricelist(ele):
    elist = {}
    elist['name'] = ele.name
    elist['teachernum'] = ele.tecnum
    elist['teamnum'] = ele.teanum
    elist['studentnum'] = ele.teanum * 3
    elist['feanum'] = ele.fnum
    elist['studentdays'] = (ele.etr_id.etime - ele.str_id.stime).days + 1
    elist['stuholdays'] = (ele.etr_id.stime - ele.str_id.etime).days + 1
    elist['ty'] = False
    if ele.eai_id:
        elist['ty'] = True
    if elist['ty']:
        elist['teacherdays'] = (ele.eai_id.etime - ele.sai_id.stime).days + 1
        elist['teajoldays'] = (ele.eai_id.stime - ele.sai_id.etime).days + 1
        elist['teas_air'] = ele.sai_id
        elist['teae_air'] = ele.eai_id
        elist['teacs_pri'] = ele.sai_id.price * elist['teachernum']
        elist['teace_pri'] = ele.eai_id.price * elist['teachernum']

    else:
        elist['teacherdays'] = elist['studentdays']
        elist['teajoldays'] = elist['stuholdays']
        elist['teas_tra'] = ele.str_id
        elist['teae_tra'] = ele.etr_id
        elist['teacs_pri'] = ele.str_id.price * elist['teachernum']
        elist['teace_pri'] = ele.etr_id.price * elist['teachernum']
    elist['stus_tra'] = ele.str_id
    elist['stue_tra'] = ele.etr_id
    elist['stus_pri'] = ele.str_id.price * elist['studentnum']
    elist['stue_pri'] = ele.etr_id.price * elist['studentnum']
    elist['acc'] = ele.ac_id
    elist['stu_acc'] = (elist['feanum'] + 1) // 2 + (elist['studentnum'] - elist['feanum'] + 1) // 2
    elist['tea_acc'] = elist['teachernum'] // 2
    if elist['teachernum'] % 2:
        if (elist['studentnum'] - elist['feanum'] + 1) % 2 == 0:
            elist['tea_acc'] += 1
    elist['stu_accpr'] = elist['stu_acc'] * ele.ac_id.price * (elist['stuholdays'] - 1)
    elist['tea_accpr'] = elist['tea_acc'] * ele.ac_id.price * (elist['teajoldays'] - 1)
    elist['allo'] = ele.allo
    elist['apply'] = ele.apply
    elist['stu_pri'] = elist['stus_pri'] + elist['stue_pri'] + elist['stu_accpr'] + ele.apply * elist['teamnum']
    elist['tea_pri'] = elist['teacs_pri'] + elist['teace_pri'] + elist['tea_accpr'] + ele.allo * elist['teajoldays'] * \
                       elist['teachernum']
    elist['price'] = elist['stu_pri'] + elist['tea_pri']
    elist['user'] = ele.ad_id.name
    return elist
def ge_nums():
    tenums = []
    teannum = []
    felnum = [0]
    for i in range(1, 10):
        tenums.append(i)
        teannum.append(i)
        felnum.append(i)
    for i in range(10, 20):
        teannum.append(i)
        felnum.append(i)
    nums = {'tenums': tenums, 'teannum': teannum, 'felnum': felnum}
    return nums
def get_price(stime, etime, site, allo):
    train = jiaotong1(stime, etime, site)
    acc1 = Acc.objects.filter(site=site)
    accc = {}
    tem = 0
    for ac in acc1:
        if (tem < ac.price):
            accc['acc'] = ac
            tem = ac.price
    price1 = 0
    if 'st_air' in train:
        tday1 = (train['end_air'].stime - train['st_air'].etime).days
        price1 = tday1 * accc['acc'].price
        tday1 = (train['end_air'].etime - train['st_air'].stime).days + 1
        price1 = price1 + tday1 * allo + (train['st_air'].price + train['end_air'].price) * 0.5
    tday2 = (train['end_train'].stime - train['st_train'].etime).days
    price2 = tday2 * accc['acc'].price
    tday2 = (train['end_train'].etime - train['st_train'].stime).days + 1
    price2 = price2 + tday2 * allo + (train['st_train'].price + train['end_train'].price)
    return (train, price1, price2, accc['acc'])
def get_name(name, site, stime, etime):
    if name == '1':
        name = 'ICPC'
    else:
        name = 'CCPC'
    with open('static/json/city.json', 'rb') as f:
        citys = json.load(f)
    cities = []
    for cit in citys.keys():
        cities = cities + citys[cit]
    site = int(site)
    site = cities[site - 1]
    if site[-1:] == '市':
        site = site[:-1]
    stime = datetime.strftime(stime, "%Y-%m-%d %H:%M")
    stime = stime.split(' ')
    etime = datetime.strftime(etime, "%Y-%m-%d %H:%M")
    etime = etime.split(' ')
    name = stime[0][:4] + name + site + "站"
    return (name, site, stime, etime)
def gt_ele(name, ele):
    can = CName.objects.create(name=name, el_id=ele)
    can.save()
    ele = pricelist(ele)
    return ele
def cre(request):
    if request.method == 'POST':
        elebform = CreForm(request.POST)  # 前端数据渲染与获取前端数据
        if elebform.is_valid():
            name = elebform.cleaned_data['nty']
            site = elebform.cleaned_data['city']
            ele = Eleb.objects.model()
            ele.tecnum = elebform.cleaned_data['teachernum']
            ele.teanum = elebform.cleaned_data['teamnum']
            ele.fnum = elebform.cleaned_data['girlnum']
            stime = elebform.cleaned_data['starttime']
            etime = elebform.cleaned_data['endtime']
            ele.allo = elebform.cleaned_data['allo']
            ele.apply = elebform.cleaned_data['apply']
            (ele.name, site, stime, etime) = get_name(name, site, stime, etime)
            Cnaser = CName.objects.filter(name=ele.name)
            if Cnaser:
                elebform = CreForm()
                return render_to_response('create.html', {'elebform': elebform, 'creerroe': True})
            else:
                ele.site = site
               #creTra(stime[0], etime[0], site)  # 12306火车车票爬虫
                #creAir(stime[0], etime[0], site)  # 携程机票爬虫
                #ceAcc(stime[0], etime[0], site)  # 美团酒店爬虫
                stime = stime[0] + " " + stime[1]
                etime = etime[0] + " " + etime[1]
                ele.stime = datetime.strptime(stime, "%Y-%m-%d %H:%M")
                ele.etime = datetime.strptime(etime, "%Y-%m-%d %H:%M")
                (train, price1, price2, accc) = get_price(ele.stime, ele.etime, site, ele.allo)
                user = LoginAdmi.objects.all()
                ele.ad_id = user[0].user
                ele.str_id = train['st_train']
                ele.etr_id = train['end_train']
                ele.ac_id = accc

                if (price1 > price2):
                    ele.sai_id = train['st_air']
                    ele.eai_id = train['end_air']

                ele.save()
                times = {'stime': ele.stime, 'etime': ele.etime}
                ele = gt_ele(ele.name, ele)
                nums = ge_nums()
                return render_to_response('e_select.html', {'ele': ele, 'nums': nums, 'times': times})
    else:
        elebform = CreForm()
    return render_to_response('create.html', {'elebform': elebform, 'creerroe': False})
def showele(request, e_id):
    ele = Eleb.objects.get(pk=e_id)
    times = {'stime': ele.stime, 'etime': ele.etime}
    ele = pricelist(ele)
    nums = ge_nums()
    return render_to_response('e_select.html', {'ele': ele, 'nums': nums, 'times': times})
def selel2(request):
    if request.is_ajax():
        name = request.POST['name']
        year = request.POST['year']
        site = request.POST['site']
        namess = []
        if name:
            elelist = Eleb.objects.filter(name=name)
            if elelist:
                for ele in elelist:
                    ele_ids = {}
                    ele_ids['nam'] = ele.name
                    ele_ids['el_id'] = ele.pk
                    namess.append(ele_ids)
                data = json.dumps(namess)
                return HttpResponse(data)
        elelist = Eleb.objects.all()
        if site:
            elelist = elelist.filter(site=site)
        if year:
            for ele in elelist:
                if ele.name[:4] == year:
                    ele_ids = {}
                    ele_ids['nam'] = ele.name
                    ele_ids['el_id'] = ele.pk
                    namess.append(ele_ids)
            data = json.dumps(namess)
            return HttpResponse(data)
        for ele in elelist:
            ele_ids = {}
            ele_ids['nam'] = ele.name
            ele_ids['el_id'] = ele.pk
            namess.append(ele_ids)
        data = json.dumps(namess)
        return HttpResponse(data)
def ajax_up_ele(request):
    if request.is_ajax():
        name = request.POST['name']
        elele = Eleb.objects.get(name=name)
        elele.tecnum = int(request.POST['teachernums'])
        elele.teanum = int(request.POST['teamnums'])
        elele.fnum = int(request.POST['felnums'])
        elele.allo = float(request.POST['allo'])
        elele.apply = float(request.POST['apply'])
        stime = request.POST['starttime']
        etime = request.POST['endtime']
        stime1 = datetime.strftime(elele.stime, "%Y-%m-%d %H:%M")
        etime1 = datetime.strftime(elele.etime, "%Y-%m-%d %H:%M")
        if stime != stime1 or etime != etime1:
            stime = stime.split(' ')
            etime = etime.split(' ')
            creTra(stime[0], etime[0], elele.site)  # 12306火车车票爬虫
            creAir(stime[0], etime[0], elele.site)  # 携程机票爬虫
            ceAcc(stime[0], etime[0], elele.site)  # 美团酒店爬虫
            stime = stime[0] + " " + stime[1]
            etime = etime[0] + " " + etime[1]
            elele.stime = datetime.strptime(stime, "%Y-%m-%d %H:%M")
            elele.etime = datetime.strptime(etime, "%Y-%m-%d %H:%M")
            (train, price1, price2, accc) = get_price(elele.stime, elele.etime, elele.site, elele.allo)
            user = LoginAdmi.objects.all()
            elele.ad_id = user[0].user
            elele.str_id = train['st_train']
            elele.etr_id = train['end_train']
            elele.ac_id = accc

            if (price1 > price2):
                elele.sai_id = train['st_air']
                elele.eai_id = train['end_air']
        elele.save()
        da = {'daa': 'Succes!'}
        da = json.dumps(da)
        return HttpResponse(da)
def ajax_de_ele(request):
    if request.is_ajax():
        name = request.POST['name']
        CName.objects.get(name=name).delete()
        Eleb.objects.get(name=name).delete()
        data = {'de_secces': '删除成功'}
        data = json.dumps(data)
        return HttpResponse(data)

def ul_list(request):
    ultlist = Ultb.objects.all()
    years = []
    for ele in ultlist:
        if ele.name[:4] not in years:
            years.append(ele.name[:4])
    sorted(years)
    creulist = CName.objects.filter(ul_id=None)
    return render_to_response('zzys.html', {'ultlist': ultlist, 'creulist': creulist, 'years': years})
def showult(request, u_id):
    ele = Ultb.objects.get(pk=u_id)
    (strtrain, endtrain) = se_traion(True, ele.stime, ele.etime, ele.site)
    (strair, endair) = se_traion(False, ele.stime, ele.etime, ele.site)
    traffics = {'strtrain': strtrain, 'endtrain': endtrain, 'strair': strair, 'endair': endair}
    grogshop = Acc.objects.filter(site=ele.site)
    ele = pricelist(ele)
    nums = ge_nums()
    creulist = CName.objects.filter(ul_id=None)
    return render_to_response('show_ult.html', {'ele': ele, 'nums': nums, 'traffics': traffics,
                                                'grogshop': grogshop, 'creulist': creulist})
def cre_ult(request, e_id):
    ele = Eleb.objects.get(pk=e_id)
    (strtrain, endtrain) = se_traion(True, ele.stime, ele.etime, ele.site)
    (strair, endair) = se_traion(False, ele.stime, ele.etime, ele.site)
    traffics = {'strtrain': strtrain, 'endtrain': endtrain, 'strair': strair, 'endair': endair}
    grogshop = Acc.objects.filter(site=ele.site)
    ele = pricelist(ele)
    nums = ge_nums()
    return render_to_response('cre_ul.html', {'ele': ele, 'e_id': e_id, 'nums': nums, 'traffics': traffics,
                                              'grogshop': grogshop})
def ajax_cre_ult(request):
    if request.is_ajax():
        ultbele = Ultb.objects.model()
        ultbele.name = request.POST['name']
        ultbele.tecnum = int(request.POST['teachernums'])
        ultbele.teanum = int(request.POST['teamnums'])
        ultbele.fnum = int(request.POST['felnums'])
        st_train = request.POST['st_train']
        ultbele.str_id = STra.objects.get(pk=st_train)
        end_train = request.POST['end_train']
        ultbele.etr_id = ETra.objects.get(pk=end_train)
        ty_traffic = request.POST['ty_traffic']
        st_teacher_traffic = request.POST['st_teacher_traffic']
        end_teacher_traffic = request.POST['end_teacher_traffic']
        hotel = request.POST['hotel']
        ultbele.ac_id = Acc.objects.get(pk=hotel)
        ultbele.allo = float(request.POST['allo'])
        ultbele.apply = float(request.POST['apply'])
        ultbele.el_id = Eleb.objects.get(name=ultbele.name)
        ultbele.stime = ultbele.el_id.stime
        ultbele.etime = ultbele.el_id.etime
        ultbele.site = ultbele.el_id.site
        ultbele.ad_id = LoginAdmi.objects.all()[0].user
        if (ty_traffic == '1'):
            ultbele.sai_id = SAir.objects.get(pk=st_teacher_traffic)
            ultbele.eai_id = EAir.objects.get(pk=end_teacher_traffic)
        ultbele.save()
        da = ultbele.pk
        cna = CName.objects.get(name=ultbele.name)
        cna.ul_id = ultbele
        cna.save()
        da = {'u_id': da}
        da = json.dumps(da)
        return HttpResponse(da)
def ajax_up_ult(request):
    if request.is_ajax():
        name = request.POST['name']
        ulele = Ultb.objects.get(name=name)
        ulele.tecnum = request.POST['teachernums']
        ulele.teanum = request.POST['teamnums']
        ulele.fnum = request.POST['felnums']
        st_train = request.POST['st_train']
        ulele.str_id = STra.objects.get(pk=st_train)
        end_train = request.POST['end_train']
        ulele.etr_id = ETra.objects.get(pk=end_train)
        ty_traffic = request.POST['ty_traffic']
        st_teacher_traffic = request.POST['st_teacher_traffic']
        end_teacher_traffic = request.POST['end_teacher_traffic']
        hotel = request.POST['hotel']
        ulele.ac_id = Acc.objects.get(pk=hotel)
        ulele.allo = request.POST['allo']
        ulele.apply = request.POST['apply']
        ulele.ad_id = LoginAdmi.objects.all()[0].user
        if (ty_traffic == '1'):
            ulele.sai_id = SAir.objects.get(pk=st_teacher_traffic)
            ulele.eai_id = EAir.objects.get(pk=end_teacher_traffic)
        ulele.save()
        da = {'daa': 'Succes!'}
        da = json.dumps(da)
        return HttpResponse(da)
def ajax_de_ult(request):
    if request.is_ajax():
        name = request.POST['name']
        CName.objects.filter(name=name).update(ul_id=None)
        Ultb.objects.get(name=name).delete()
        data = {'de_secces': '删除成功'}
        data = json.dumps(data)
        return HttpResponse(data)
def ajax_se_ult(request):
    if request.is_ajax():
        name = request.POST['name']
        year = request.POST['year']
        site = request.POST['site']
        namess = []
        if name:
            elelist = Ultb.objects.filter(name=name)
            if elelist:
                for ele in elelist:
                    ele_ids = {}
                    ele_ids['nam'] = ele.name
                    ele_ids['el_id'] = ele.pk
                    namess.append(ele_ids)
                data = json.dumps(namess)
                return HttpResponse(data)
        elelist = Ultb.objects.all()
        if site:
            elelist = elelist.filter(site=site)
        if year:
            for ele in elelist:
                if ele.name[:4] == year:
                    ele_ids = {}
                    ele_ids['nam'] = ele.name
                    ele_ids['el_id'] = ele.pk
                    namess.append(ele_ids)
            data = json.dumps(namess)
            return HttpResponse(data)
        for ele in elelist:
            ele_ids = {}
            ele_ids['nam'] = ele.name
            ele_ids['el_id'] = ele.pk
            namess.append(ele_ids)
        data = json.dumps(namess)
        return HttpResponse(data)

def account_list(request):
    acclist = Account.objects.all()
    years = []
    for ele in acclist:
        if ele.name[:4] not in years:
            years.append(ele.name[:4])
    sorted(years)
    crealist = CName.objects.filter(ac_id=None, ul_id__isnull=False)
    return render_to_response('accou.html', {'acclist': acclist, 'crealist': crealist, 'years': years})
def cre_account(request, u_id):
    ele = Ultb.objects.get(pk=u_id)
    (strtrain, endtrain) = se_traion(True, ele.stime, ele.etime, ele.site)
    (strair, endair) = se_traion(False, ele.stime, ele.etime, ele.site)
    traffics = {'strtrain': strtrain, 'endtrain': endtrain, 'strair': strair, 'endair': endair}
    grogshop = Acc.objects.filter(site=ele.site)
    ele = pricelist(ele)
    nums = ge_nums()
    return render_to_response('cre_acco.html', {'ele': ele, 'nums': nums, 'traffics': traffics,
                                                'grogshop': grogshop})
def ajax_cre_account(request):
    if request.is_ajax():
        acco = Account.objects.model()
        acco.name = request.POST['name']
        acco.tecnum = int(request.POST['teachernums'])
        acco.teanum = int(request.POST['teamnums'])
        acco.fnum = int(request.POST['felnums'])
        st_train = request.POST['st_train']
        acco.str_id = STra.objects.get(pk=st_train)
        end_train = request.POST['end_train']
        acco.etr_id = ETra.objects.get(pk=end_train)
        ty_traffic = request.POST['ty_traffic']
        st_teacher_traffic = request.POST['st_teacher_traffic']
        end_teacher_traffic = request.POST['end_teacher_traffic']
        hotel = request.POST['hotel']
        acco.ac_id = Acc.objects.get(pk=hotel)
        acco.allo = float(request.POST['allo'])
        acco.apply = float(request.POST['apply'])
        acco.comm = request.POST['comm']
        acco.ul_id = CName.objects.get(name=acco.name).ul_id
        acco.stime = acco.ul_id.stime
        acco.etime = acco.ul_id.etime
        acco.site = acco.ul_id.site
        acco.ad_id = LoginAdmi.objects.all()[0].user
        if (ty_traffic == '1'):
            acco.sai_id = SAir.objects.get(pk=st_teacher_traffic)
            acco.eai_id = EAir.objects.get(pk=end_teacher_traffic)
        acco.save()
        da = acco.pk
        cna = CName.objects.get(name=acco.name)
        cna.ac_id = acco
        cna.save()
        da = {'acco_id': da}
        da = json.dumps(da)
        return HttpResponse(da)
def show_account(request, acco_id):
    ele = Account.objects.get(pk=acco_id)
    comm = ele.comm
    (strtrain, endtrain) = se_traion(True, ele.stime, ele.etime, ele.site)
    (strair, endair) = se_traion(False, ele.stime, ele.etime, ele.site)
    traffics = {'strtrain': strtrain, 'endtrain': endtrain, 'strair': strair, 'endair': endair}
    grogshop = Acc.objects.filter(site=ele.site)
    ele = pricelist(ele)
    nums = ge_nums()
    crealist = CName.objects.filter(ac_id=None, ul_id__isnull=False)
    return render_to_response('show_acco.html', {'ele': ele, 'nums': nums, 'traffics': traffics,
                                                 'grogshop': grogshop, 'comm': comm, 'crealist': crealist})
def ajax_up_account(request):
    if request.is_ajax():
        name = request.POST['name']
        acco = Account.objects.get(name=name)
        acco.tecnum = request.POST['teachernums']
        acco.teanum = request.POST['teamnums']
        acco.fnum = request.POST['felnums']
        st_train = request.POST['st_train']
        acco.str_id = STra.objects.get(pk=st_train)
        end_train = request.POST['end_train']
        acco.etr_id = ETra.objects.get(pk=end_train)
        ty_traffic = request.POST['ty_traffic']
        st_teacher_traffic = request.POST['st_teacher_traffic']
        end_teacher_traffic = request.POST['end_teacher_traffic']
        hotel = request.POST['hotel']
        acco.ac_id = Acc.objects.get(pk=hotel)
        acco.allo = request.POST['allo']
        acco.apply = request.POST['apply']
        acco.ad_id = LoginAdmi.objects.all()[0].user
        acco.comm = request.POST['comm']
        if (ty_traffic == '1'):
            acco.sai_id = SAir.objects.get(pk=st_teacher_traffic)
            acco.eai_id = EAir.objects.get(pk=end_teacher_traffic)
        acco.save()
        da = {'daa': 'Succes!'}
        da = json.dumps(da)
        return HttpResponse(da)
def ajax_se_account(request):
    if request.is_ajax():
        name = request.POST['name']
        year = request.POST['year']
        site = request.POST['site']
        namess = []
        if name:
            elelist = Account.objects.filter(name=name)
            if elelist:
                for ele in elelist:
                    ele_ids = {}
                    ele_ids['nam'] = ele.name
                    ele_ids['el_id'] = ele.pk
                    namess.append(ele_ids)
                data = json.dumps(namess)
                return HttpResponse(data)
        elelist = Account.objects.all()
        if site:
            elelist = elelist.filter(site=site)
        if year:
            for ele in elelist:
                if ele.name[:4] == year:
                    ele_ids = {}
                    ele_ids['nam'] = ele.name
                    ele_ids['el_id'] = ele.pk
                    namess.append(ele_ids)
            data = json.dumps(namess)
            return HttpResponse(data)
        for ele in elelist:
            ele_ids = {}
            ele_ids['nam'] = ele.name
            ele_ids['el_id'] = ele.pk
            namess.append(ele_ids)
        data = json.dumps(namess)
        return HttpResponse(data)
def ajax_de_account(request):
    if request.is_ajax():
        name = request.POST['name']
        CName.objects.filter(name=name).update(ac_id=None)
        Account.objects.get(name=name).delete()
        data = {'de_secces': '删除成功'}
        data = json.dumps(data)
        return HttpResponse(data)
def accountyear(request, year):
    year = str(year)
    elelist = Account.objects.all()
    eleslist = []
    prices = 0
    for ele in elelist:
        if (ele.name[0:4] == year):
            price = {}
            pri_acc = (ele.etr_id.stime - ele.str_id.etime).days * ele.ac_id.price
            price['stu_accpri'] = ((ele.fnum + 1) // 2 + (ele.teanum * 3 - ele.fnum + 1) // 2) * pri_acc
            price['stu_traionpri'] = (ele.str_id.price + ele.etr_id.price) * ele.teanum * 3
            price['stu_apply'] = ele.apply * ele.teanum
            price['te_traionpri'] = (ele.str_id.price + ele.etr_id.price) * ele.tecnum
            price['stu_num'] = ele.teanum
            te_acc = ele.tecnum // 2
            te_day = (ele.etr_id.etime - ele.str_id.stime).days + 1
            price['is_air'] = False
            if ele.tecnum % 2:
                if (ele.teanum * 3 - ele.fnum) % 2 == 0:
                    te_acc += 1
            if ele.sai_id != None:
                price['is_air'] = True
                pri_acc = (ele.eai_id.stime - ele.sai_id.etime).days * ele.ac_id.price
                te_day = (ele.eai_id.etime - ele.sai_id.stime).days + 1
                price['te_traionpri'] = (ele.eai_id.price + ele.sai_id.price) * ele.tecnum
            price['te_accpri'] = te_acc * pri_acc
            price['te_allo'] = ele.allo * te_day * ele.tecnum
            price['te_nums'] = ele.tecnum
            price['te_price'] = price['te_traionpri'] + price['te_accpri'] + price['te_allo']
            price['stu_price'] = price['stu_traionpri'] + price['stu_accpri'] + price['stu_apply']
            price['pri'] = price['te_price'] + price['stu_price']
            price['name'] = ele.name
            eles = {'price': price}
            eleslist.append(eles)
            prices += price['pri']
    return render_to_response('accoyear.html', {'eleslist': eleslist, 'prices': prices, 'year': year})

def show_qt(request, type):
    if type == 1:
        elelist = STra.objects.all()
        naty = '出发车次'
    elif type == 2:
        elelist = ETra.objects.all()
        naty = '回程车次'
    elif type == 3:
        elelist = SAir.objects.all()
        naty = '出发航班'
    elif type == 4:
        elelist = EAir.objects.all()
        naty = '回程航班'
    else:
        elelist = Acc.objects.all()
        naty = '酒店'
    return render_to_response('qt_list.html', {'elelist': elelist, 'type': type, 'naty': naty})
def ajax_se_qt(request):
    if request.is_ajax():
        time = request.POST['time']
        tra_id = request.POST['tra_id']
        site = request.POST['site']
        type = request.POST['type']
        data = []
        if type == '1':
            elelist = STra.objects.all()
            if tra_id:
                elelist = elelist.filter(T_id=tra_id)
            if site:
                elelist = elelist.filter(site=site)
            for ele in elelist:
                if time:
                    stime = datetime.strftime(ele.stime, "%Y-%m-%d %H:%M")
                    stime = stime.split(' ')
                    if stime[0] != time:
                        continue
                das = {'pk':ele.pk,'T_id': ele.T_id, 'site': ele.site, 'stime': ele.stime, 'etime': ele.etime, 'price': ele.price}
                data.append(das)
            data = json.dumps(data,cls=DateEncoder)
            return HttpResponse(data)
        elif type == '2':
            elelist = ETra.objects.all()
            if tra_id:
                elelist = elelist.filter(T_id=tra_id)
            if site:
                elelist = elelist.filter(site=site)
            for ele in elelist:
                if time:
                    etime = datetime.strftime(ele.etime, "%Y-%m-%d %H:%M")
                    etime = etime.split(' ')
                    if etime[0] != time:
                        continue
                das = {'pk':ele.pk,'T_id': ele.T_id, 'site': ele.site, 'stime': ele.stime, 'etime': ele.etime, 'price': ele.price}
                data.append(das)
            data = json.dumps(data,cls=DateEncoder)
            return HttpResponse(data)
        elif type == '3':
            elelist = SAir.objects.all()
            if tra_id:
                elelist = elelist.filter(A_id=tra_id)
            if site:
                elelist = elelist.filter(site=site)
            for ele in elelist:
                if time:
                    stime = datetime.strftime(ele.stime, "%Y-%m-%d %H:%M")
                    stime = stime.split(' ')
                    if stime[0] != time:
                        continue
                das = {'pk': ele.pk,'A_id': ele.A_id, 'site': ele.site, 'stime': ele.stime, 'etime': ele.etime, 'price': ele.price}
                data.append(das)
            data = json.dumps(data, cls=DateEncoder)
            return HttpResponse(data)
        elif type == '4':
            elelist = EAir.objects.all()
            if tra_id:
                elelist = elelist.filter(A_id=tra_id)
            if site:
                elelist = elelist.filter(site=site)
            for ele in elelist:
                if time:
                    etime = datetime.strftime(ele.etime, "%Y-%m-%d %H:%M")
                    etime = etime.split(' ')
                    if etime[0] != time:
                        continue
                das = {'pk': ele.pk,'A_id':ele.A_id, 'site': ele.site, 'stime': ele.stime, 'etime': ele.etime, 'price': ele.price}
                data.append(das)
            data = json.dumps(data,cls=DateEncoder)
            return HttpResponse(data)
        else:
            elelist = Acc.objects.all()
            if tra_id:
                elelist = elelist.filter(name=tra_id)
            if site:
                elelist = elelist.filter(site=site)
            for ele in elelist:
                das = {'pk':ele.pk,'name': ele.name, 'site': ele.site, 'price': ele.price}
                data.append(das)
            data = json.dumps(data)
            return HttpResponse(data)
def ajax_cre_qt(request):
    if request.is_ajax():
        cre_tra_id = request.POST['cre_tra_id']
        type = request.POST['type']
        cre_site = request.POST['cre_site']
        cre_price = request.POST['cre_price']
        cre_stime = request.POST['cre_stime']
        cre_etime = request.POST['cre_etime']
        if type == '1':
            cre_stime = datetime.strptime(cre_stime, "%Y-%m-%d %H:%M")
            cre_etime = datetime.strptime(cre_etime, "%Y-%m-%d %H:%M")
            STra.objects.create(T_id=cre_tra_id, site=cre_site, price=cre_price, stime=cre_stime, etime=cre_etime)
        elif type == '2':
            cre_stime = datetime.strptime(cre_stime, "%Y-%m-%d %H:%M")
            cre_etime = datetime.strptime(cre_etime, "%Y-%m-%d %H:%M")
            ETra.objects.create(T_id=cre_tra_id, site=cre_site, price=cre_price, stime=cre_stime, etime=cre_etime)
        elif type == '3':
            cre_stime = datetime.strptime(cre_stime, "%Y-%m-%d %H:%M")
            cre_etime = datetime.strptime(cre_etime, "%Y-%m-%d %H:%M")
            SAir.objects.create(A_id=cre_tra_id, site=cre_site, price=cre_price, stime=cre_stime, etime=cre_etime)
        elif type == '4':
            cre_stime = datetime.strptime(cre_stime, "%Y-%m-%d %H:%M")
            cre_etime = datetime.strptime(cre_etime, "%Y-%m-%d %H:%M")
            EAir.objects.create(A_id=cre_tra_id, site=cre_site, price=cre_price, stime=cre_stime, etime=cre_etime)
        else:
            Acc.objects.create(name=cre_tra_id, site=cre_site, price=cre_price)
        data = {'hh': '创建成功'}
        data = json.dumps(data)
        return HttpResponse(data)
def ajax_de_qt(request):
    if request.is_ajax():
        de_idlist = request.POST.getlist('de_idlist')
        type = request.POST['type']
        data = {}
        data['de_succes'] = True
        if type == '1':
            for de_id in de_idlist:
                try:
                    STra.objects.get(pk=de_id).delete()
                except:
                    data['de_succes'] = False
        elif type == '2':
            for de_id in de_idlist:
                try:
                    ETra.objects.get(pk=de_id).delete()
                except:
                    data['de_succes'] = False
        elif type == '3':
            for de_id in de_idlist:
                try:
                    SAir.objects.get(pk=de_id).delete()
                except:
                    data['de_succes'] = False
        elif type == '4':
            for de_id in de_idlist:
                try:
                    EAir.objects.get(pk=de_id).delete()
                except:
                    data['de_succes'] = False
        else:
            for de_id in de_idlist:
                try:
                    Acc.objects.get(pk=de_id).delete()
                except:
                    data['de_succes'] = False
        data = json.dumps(data)
        return HttpResponse(data)
