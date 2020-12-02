from django.contrib import admin
from django.forms import ModelForm

from account.models import User


# Register your models here.

class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['inviter'].queryset = User.objects.filter(id=self.instance.id).all()


class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'create_time', 'modify_time', 'current_level', 'new_withdraw', 'cash')
    search_fields = ('name',)
    form = UserForm


admin.site.register(User, UserAdmin)
