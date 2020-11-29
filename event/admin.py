# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from event.models import AdEvent, ObjectEvent


class AdEventAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'ad_type', 'channel', 'create_time', 'modify_time', 'extra')
    search_fields = ('user_id', 'ad_type')


class ObjectEventAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'action', 'object', 'create_time', 'modify_time', 'extra')
    search_fields = ('user_id', 'object')


admin.site.register(AdEvent, AdEventAdmin)
admin.site.register(ObjectEvent, ObjectEventAdmin)
