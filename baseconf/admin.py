from django.contrib import admin
from baseconf.models import *


# Register your models here.

class ABTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'create_time', 'status', 'traffic',)
    search_fields = ('name', 'slug')


admin.site.register(GlobalConf)
admin.site.register(PageConf)
admin.site.register(WithdrawConf)
admin.site.register(ABTest, ABTestAdmin)
