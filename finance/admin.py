from django.contrib import admin
from finance.models import *
# Register your models here.

admin.site.register(ExchangeRecord)
admin.site.register(RedPacket)


class CashRecordAdmin(admin.ModelAdmin):
    list_display = ('belong.name', 'cash', 'create_time', 'status', 'reason')
    search_fields = ('belong',)


admin.site.register(CashRecord)
