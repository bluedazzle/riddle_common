from django.contrib import admin
from account.models import User

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'create_time', 'current_level', 'new_withdraw', 'cash')
    search_fields = ('name',)


admin.site.register(User, UserAdmin)
