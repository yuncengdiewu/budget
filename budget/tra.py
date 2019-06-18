# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import requests
import json
from .models import STra, ETra


def get_train_info(t, arr):
    tralist = []
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep - alive',
            'Content-Type': 'text/javascript;charset = UTF - 8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init'
            }
    with open('static/json/stations.json', 'rb') as f:
        station = json.load(f)
    url = 'https://kyfw.12306.cn/otn/leftTicket/query?' \
          'leftTicketDTO.train_date={}&' \
          'leftTicketDTO.from_station={}&' \
          'leftTicketDTO.to_station={}' \
          '&purpose_codes=ADULT'.format(
        t, station['成都'], station[arr])
    s = requests.session()
    r = s.get(url, headers=head, verify=False)
    try:
        r = json.loads(r.text)
        infos = r['data']['result']
        i = 1
        for info in infos:
            info = info.split('|')[2:]
            if info[28] == '有' or info[26] == '有':
                tra = {'T_id': info[1], 'stime': info[6], 'etime': info[7], 'ltime': info[8]}
                price_url = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?' \
                        'train_no={}&' \
                        'from_station_no={}&' \
                        'to_station_no={}&' \
                        'seat_types={}&' \
                        'train_date={}'.format(info[0], info[14], info[15], info[33], t)
                s = requests.session()
                pr = s.get(price_url, headers=head, verify=False)
                pr = json.loads(pr.text)
                if info[28] == '有':
                    if 'O' not in pr['data'].keys():
                        continue
                    pr = pr['data']['O']
                elif 'A3' in pr['data'].keys():
                    pr = pr['data']['A3']
                else:
                    continue
                pr = pr[1:]
                pr = float(pr)
                tra.update({'price': pr})
                tralist.append(tra)
            pass
    except:
        return
    return tralist


def creTra(st, et, stat):
    with open('static/json/stations.json', 'rb') as f:
        station = json.load(f)
    if stat not in station.keys():
        return
    miday = 100
    maday = 0

    etralist = get_train_info(et, stat)
    for etra in etralist:
        stim = etra['stime'].split(':')
        stim[0] = int(stim[0])
        stim[1] = int(stim[1])
        ltime = etra['ltime'].split(':')
        ltime[0] = int(ltime[0])
        ltime[1] = int(ltime[1])
        tim = []
        tim.append(stim[0] + ltime[0])
        tim.append(stim[1] + ltime[1])
        tim[0] += tim[1] // 60
        da = tim[0] // 24
        if (miday > da):
            miday = da
        if (maday < da):
            maday = da
        if maday < 1:
            maday = 1
        etra['stime'] = et + ' ' + etra['stime']
        etra['stime'] = datetime.strptime(etra['stime'], "%Y-%m-%d %H:%M")
        etra['etime'] = et + ' ' + etra['etime']
        etime = etra['etime']
        etime = datetime.strptime(etime, "%Y-%m-%d %H:%M")
        etime = etime + timedelta(days=da)
        etra['etime'] = etime
        ETrrname = ETra.objects.filter(T_id=etra['T_id'], stime=etra['stime'], etime=etra['etime'], site=stat)
        if ETrrname:
            ETrrname.update(price=etra['price'])
        else:
            ETra.objects.create(T_id=etra['T_id'], stime=etra['stime'], etime=etra['etime'], price=etra['price'],
                            site=stat)
    et = datetime.strptime(et, "%Y-%m-%d")
    et = et + timedelta(days=1)
    et = datetime.strftime(et, "%Y-%m-%d")
    etralist = get_train_info(et, stat)
    for etra in etralist:
        stim = etra['stime'].split(':')
        stim[0] = int(stim[0])
        stim[1] = int(stim[1])
        ltime = etra['ltime'].split(':')
        ltime[0] = int(ltime[0])
        ltime[1] = int(ltime[1])
        tim = []
        tim.append(stim[0] + ltime[0])
        tim.append(stim[1] + ltime[1])
        tim[0] += tim[1] // 60
        da = tim[0] // 24
        etra['stime'] = et + ' ' + etra['stime']
        etra['stime'] = datetime.strptime(etra['stime'], "%Y-%m-%d %H:%M")
        etra['etime'] = et + ' ' + etra['etime']
        etime = etra['etime']
        etime = datetime.strptime(etime, "%Y-%m-%d %H:%M")
        etime = etime + timedelta(days=da)
        etra['etime'] = etime
        ETrrname = ETra.objects.filter(T_id=etra['T_id'], stime=etra['stime'], etime=etra['etime'], site=stat)
        if ETrrname:
            ETrrname.update(price=etra['price'])
        else:
            ETra.objects.create(T_id=etra['T_id'], stime=etra['stime'], etime=etra['etime'], price=etra['price'],
                            site=stat)


    st = datetime.strptime(st, "%Y-%m-%d")
    st = st - timedelta(days=miday)
    st = datetime.strftime(st, "%Y-%m-%d")
    etralist = get_train_info(st, stat)
    for etra in etralist:
        stim = etra['stime'].split(':')
        stim[0] = int(stim[0])
        stim[1] = int(stim[1])
        ltime = etra['ltime'].split(':')
        ltime[0] = int(ltime[0])
        ltime[1] = int(ltime[1])
        tim = []
        tim.append(stim[0] + ltime[0])
        tim.append(stim[1] + ltime[1])
        tim[0] += tim[1] // 60
        da = tim[0] // 24
        etra['stime'] = st + ' ' + etra['stime']
        etra['stime'] = datetime.strptime(etra['stime'], "%Y-%m-%d %H:%M")
        etra['etime'] = st + ' ' + etra['etime']
        etime = etra['etime']
        etime = datetime.strptime(etime, "%Y-%m-%d %H:%M")
        etime = etime + timedelta(days=da)
        etra['etime'] = etime
        STrrname = STra.objects.filter(T_id=etra['T_id'], stime=etra['stime'], etime=etra['etime'], site=stat)
        if STrrname:
            STrrname.update(price=etra['price'])
        else:
            STra.objects.create(T_id=etra['T_id'], stime=etra['stime'], etime=etra['etime'], price=etra['price'],
                        site=stat)
    if maday < 1:
        maday = 1
    if maday > miday:
        st = datetime.strptime(st, "%Y-%m-%d")
        st = st - timedelta(days=maday)
        st = datetime.strftime(st, "%Y-%m-%d")
        etralist = get_train_info(st, stat)
        for etra in etralist:
            stim = etra['stime'].split(':')
            stim[0] = int(stim[0])
            stim[1] = int(stim[1])
            ltime = etra['ltime'].split(':')
            ltime[0] = int(ltime[0])
            ltime[1] = int(ltime[1])
            tim = []
            tim.append(stim[0] + ltime[0])
            tim.append(stim[1] + ltime[1])
            tim[0] += tim[1] // 60
            da = tim[0] // 24
            etra['stime'] = st + ' ' + etra['stime']
            etra['stime'] = datetime.strptime(etra['stime'], "%Y-%m-%d %H:%M")
            etra['etime'] = st + ' ' + etra['etime']
            etime = etra['etime']
            etime = datetime.strptime(etime, "%Y-%m-%d %H:%M")
            etime = etime + timedelta(days=da)
            etra['etime'] = etime
            STrrname = STra.objects.filter(T_id=etra['T_id'], stime=etra['stime'], etime=etra['etime'], site=stat)
            if STrrname:
                STrrname.update(price=etra['price'])
            else:
                STra.objects.create(T_id=etra['T_id'], stime=etra['stime'], etime=etra['etime'], price=etra['price'],
                        site=stat)
