# -*- coding:utf-8 -*-
import requests
import json
from .peizhi import *
import re
from xpinyin import Pinyin
from .models import Acc

def get_airport_info(city, st, et,page=1):
    head = {'Accept':'application/json,text/plain,*/*',
            'Origin':'https://hotel.meituan.com',
            'Referer':'https://hotel.meituan.com/beijing/',
            'User-Agent':'Mozilla/5.0(WindowsNT6.1;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/72.0.3626.121Safari/537.36',
            }
    hot = []
    p = Pinyin()
    s = requests.session()
    r = s.get('https://hotel.meituan.com/'+p.get_pinyin(city).replace('-','')+'/',headers=head, verify=False)
    id = re.search('"cityId".+?,',r.text).group()[9:-1]
    url = 'https://ihotel.meituan.com/hbsearch/HotelSearch?utm_medium=pc&version_name=999.9&cateId=20&attr_28=129&uuid=D6A966CD095BE61B97D64D5E1600D132BDF518CEF965A433C907DDB2BAD153DB%401556970798856&cityId={}&offset={}&limit=50&startDay={}&endDay={}&q=&sort=defaults&X-FOR-WITH=oTN8zFwUHJVTqnqi594kHZJIlZOEfLsCSy%2BUmjgeL3LQ%2FlwPwYWUsyPLnScJrK50QgCQ%2B2nrgfA5SVwU3sV%2FVvxOsSeeWK6pKkW3BaP1B5Id2xRx2g4wIMzbBU9UyvHp4KjSviOVI6A3j21BzBFRpQ%3D%3D'.format(id,page*50,st,et)
    r = s.get(url,headers=head, verify=False)
    print(r)
    r = json.loads(r.text)
    for hh in r['data']['searchresult']:
        hel = {'name': hh['name'], 'price':hh['originalPrice']}
        hot.append(hel)
    return hot

def ceAcc(st, et, stat):
    st = st[:4] + st[5:7] + st[-2:]
    et = et[:4] + et[5:7] + et[-2:]
    hotellist = get_airport_info(stat,st,et)
    for hotel in hotellist:
        accname = Acc.objects.filter(name=hotel['name'])
        if accname:
            accname.update(site=stat, price=hotel['price'])
        else:
            Acc.objects.create(name=hotel['name'], site=stat, price=hotel['price'])
