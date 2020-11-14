from django.contrib import admin
from question.models import Song, Question, Girl

# Register your models here.

admin.site.register(Song)
admin.site.register(Girl)
admin.site.register(Question)
