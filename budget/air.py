# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import requests
import json
from .models import SAir, EAir
from .peizhi import *


def get_airport_info(t, arr):
    dep = '成都'
    d = []
    head = {'Host': 'flights.ctrip.com',
            'Connection': 'keep-alive',
            'Content-Length': '224',
            'Origin': 'https://flights.ctrip.com',
            'User-Agent': 'Mozilla/5.0(WindowsNT6.1;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/72.0.3626.121Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Referer': 'https://flights.ctrip.com/itinerary/oneway/szx-bjs',
            'Accept-Encoding': 'gzip,deflate,br',
            'Accept-Language': 'zh-CN,zh;q=0.9', }
    url = 'https://flights.ctrip.com/itinerary/api/12808/products'
    data = {"flightWay": "Oneway", "classType": "ALL", "hasChild": 'false', "hasBaby": 'false', "searchIndex": 1,
            "airportParams": [
                {"dcity": code[dep][-3:], "acity": code[arr][-3:], "dcityname": dep, "acityname": arr, "date": t,
                 "dcityid": 30, "acityid": 1}]}
    s = requests.session()
    r = s.post(url, data=json.dumps(data), headers=head, verify=False)
    r = json.loads(r.text)
    for i in r['data']['routeList']:
        j = 1
        if 'flight' in i['legs'][0].keys():
            j = 0
        airr = {'A_id': i['legs'][j]['flight']['flightNumber'],
                'stime': i['legs'][j]['flight']['departureDate'],
                'etime': i['legs'][j]['flight']['arrivalDate'], }
        if i['legs'][j]['characteristic']['lowestPrice']:
            airr['price'] = i['legs'][j]['characteristic']['lowestPrice']
        elif i['transitPrice']:
            airr['price'] = i['transitPrice']
        else:
            continue
        d.append(airr)
    return d


def creAir(st, et, stat):
    if stat not in code:
        return
    aiirlist = get_airport_info(et, stat)
    maday = 0
    for airr in aiirlist:
        airr['etime'] = datetime.strptime(airr['etime'][:-3], "%Y-%m-%d %H:%M")
        airr['stime'] = datetime.strptime(airr['stime'][:-3], "%Y-%m-%d %H:%M")
        print(airr['price'])
        Eairname = EAir.objects.filter(A_id=airr['A_id'], stime=airr['stime'], etime=airr['etime'], site=stat)
        if Eairname:
            Eairname.update(price=airr['price'])
        else:
            EAir.objects.create(A_id=airr['A_id'], stime=airr['stime'], etime=airr['etime'], price=airr['price'], site=stat)
        if (airr['etime'].year != airr['stime'].year
                or airr['etime'].month != airr['stime'].month
                or airr['etime'].day != airr['stime'].day):
            maday = 1
    et = datetime.strptime(et, "%Y-%m-%d")
    et = et + timedelta(days=1)
    et = datetime.strftime(et, "%Y-%m-%d")
    aiirlist = get_airport_info(et, stat)
    for airr in aiirlist:
        airr['etime'] = datetime.strptime(airr['etime'][:-3], "%Y-%m-%d %H:%M")
        airr['stime'] = datetime.strptime(airr['stime'][:-3], "%Y-%m-%d %H:%M")
        Eairname = EAir.objects.filter(A_id=airr['A_id'], stime=airr['stime'], etime=airr['etime'], site=stat)
        if Eairname:
            Eairname.update(price=airr['price'])
        else:
            EAir.objects.create(A_id=airr['A_id'], stime=airr['stime'], etime=airr['etime'], price=airr['price'], site=stat)
    aiirlist = get_airport_info(st, stat)
    for airr in aiirlist:
        airr['etime'] = datetime.strptime(airr['etime'][:-3], "%Y-%m-%d %H:%M")
        airr['stime'] = datetime.strptime(airr['stime'][:-3], "%Y-%m-%d %H:%M")
        Sairname = SAir.objects.filter(A_id=airr['A_id'], stime=airr['stime'], etime=airr['etime'], site=stat)
        if Sairname:
            Sairname.update(price=airr['price'])
        else:
            SAir.objects.create(A_id=airr['A_id'], stime=airr['stime'], etime=airr['etime'], price=airr['price'], site=stat)
    if maday > 0:
        st = datetime.strptime(st, "%Y-%m-%d")
        st = st - timedelta(days=1)
        st = datetime.strftime(st, "%Y-%m-%d")
        aiirlist = get_airport_info(st, stat)
        for airr in aiirlist:
            airr['etime'] = datetime.strptime(airr['etime'][:-3], "%Y-%m-%d %H:%M")
            airr['stime'] = datetime.strptime(airr['stime'][:-3], "%Y-%m-%d %H:%M")
            Sairname = SAir.objects.filter(A_id=airr['A_id'], stime=airr['stime'], etime=airr['etime'], site=stat)
            if Sairname:
                Sairname.update(price=airr['price'])
            else:
                SAir.objects.create(A_id=airr['A_id'], stime=airr['stime'], etime=airr['etime'], price=airr['price'],
                                site=stat)
