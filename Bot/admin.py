from django.contrib import admin
from .models import Appl, Client, Message


@admin.register(Appl)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('DateStart', 'DateStop', 'employee_close')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_username', 'app')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('time', 'text', 'metadata', 'app')
