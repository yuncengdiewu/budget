from django.contrib import admin
from .models import STra, ETra, CName, Account, SAir, Acc, Eleb, Ultb, Admi, EAir

@admin.register(STra)
class STra(admin.ModelAdmin):
    list_display = ('T_id', 'stime', 'etime', 'price', 'site')

@admin.register(ETra)
class STra(admin.ModelAdmin):
    list_display = ('T_id', 'stime', 'etime', 'price', 'site')

@admin.register(Acc)
class Accom(admin.ModelAdmin):
    list_display = ('name', 'price')

@admin.register(Account)
class Acco(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(SAir)
class SAirp(admin.ModelAdmin):
    list_display = ('id', 'price')

@admin.register(EAir)
class Eirp(admin.ModelAdmin):
    list_display = ('id', 'price')


@admin.register(Eleb)
class Elebud(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Ultb)
class Ultbud(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(CName)
class Cname(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Admi)
class Admins(admin.ModelAdmin):
    list_display = ('id', 'name', 'password', 'ty')