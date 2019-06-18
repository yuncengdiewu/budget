import json
from datetime import datetime, timedelta
from django import forms
from .models import Admi,CName

class LoginForm(forms.Form):
    username = forms.CharField(label='账号', max_length=15, required=True, min_length=3,
                               widget=forms.TextInput(),
                               error_messages={
                                   'required': '请填写你的用户名',
                                   'max_length': '最多只能输入15个字符',
                                   'min_length': '至少输入3个字符'})
    password = forms.CharField(label='密码', max_length=20, min_length=3, required=True,
                               widget=forms.PasswordInput(),
                               error_messages={
                                   'required': '请输入密码',
                                   'max_length': '最多只能输入20个字符',
                                   'min_length': '至少输入3个字符'},
                               )
    def clean_username(self):
        user = self.cleaned_data['username']
        try:
            UserModal = Admi.objects.get(name=user)
            return user
        except:
           raise forms.ValidationError("账号不存在")

class CreForm(forms.Form):
    with open('static/json/city.json', 'rb') as f:
        city = json.load(f)
    PROVINCE_CHOICES = []
    CITY_CHOICES = []
    i = 1
    j = 1
    for ci in city.keys():
        PROVINCE_CHOICES.append([i, ci])
        for cit in city[ci]:
            CITY_CHOICES.append([j, cit])
            j += 1
        i += 1
    nty = forms.CharField(label='比赛类型', initial=2,
                           widget=forms.Select(choices=((1, 'ICPC'), (2, 'CCPC'),), attrs={'class': 'form-control'}))
    city = forms.ChoiceField(label='选择市',choices=CITY_CHOICES,
                             widget=forms.Select( attrs={'class': 'select form-control'}))
    province = forms.ChoiceField(choices=PROVINCE_CHOICES, label='选择省',
        widget=forms.Select(attrs={'class': 'select form-control', 'onChange': 'getCityOptions(this.value)'}))

    teachernum = forms.IntegerField(label='老师数量',min_value=1, max_value=50,
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    teamnum = forms.IntegerField(label='队伍数量', min_value=1, max_value=50,
                                 widget=forms.NumberInput(attrs={'class' : 'form-control'}))
    girlnum = forms.IntegerField(label='女性数量', min_value=0, max_value= 50,
                                 widget=forms.NumberInput(attrs={'class' : 'form-control'}))
    starttime = forms.DateTimeField(label='到达时间', widget=forms.TextInput(attrs={'class': 'form-control datetimepicker'}))
    endtime = forms.DateTimeField(label='回程时间', widget=forms.TextInput(attrs={'class': 'form-control datetimepicker'}))
    allo = forms.FloatField(label='补贴', widget=forms.TextInput(attrs={'class' : 'form-control', 'value': '100'}),)
    apply = forms.FloatField(label='报名费', widget=forms.TextInput(attrs={'class' : 'form-control', 'value': '1500'}))


