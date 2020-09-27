# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from event.models import AdEvent


class AdEventAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'ad_type', 'channel', 'create_time', 'modify_time', 'extra')
    search_fields = ('user_id', 'ad_type')

admin.site.register(AdEvent, AdEventAdmin)
