"""Riddle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/user/', include('account.urls')),
    url(r'^api/v1/finance/', include('finance.urls')),
    url(r'^api/v1/base/', include('baseconf.urls')),
    url(r'^api/v1/question/', include('question.urls')),
    url(r'^api/v1/event/', include('event.urls')),
    url(r'^api/v1/task/', include('task.urls')),
    url('', include('django_prometheus.urls')),
]
