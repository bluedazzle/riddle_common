from django.db import models

# Create your models here.
from account.models import User, BaseModel
from django_prometheus.models import ExportModelOperationsMixin


class CommonTask(ExportModelOperationsMixin("CommonTask"), BaseModel):
    task_id = models.CharField(max_length=200, unique=True)
    slug = models.CharField(max_length=50)
    detail = models.TextField(max_length=256, null=True, blank=True)
    belong_id = models.IntegerField()

    def __unicode__(self):
        return self.task_id

    def __str__(self):
        return self.task_id


class DailyTask(ExportModelOperationsMixin("DailyTask"), BaseModel):
    task_id = models.CharField(max_length=200, unique=True)
    slug = models.CharField(max_length=50)
    detail = models.TextField(max_length=256, null=True, blank=True)
    belong_id = models.IntegerField()

    def __unicode__(self):
        return self.task_id

    def __str__(self):
        return self.task_id
