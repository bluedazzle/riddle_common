# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.views.generic import CreateView

from core.Mixin.JsonRequestMixin import JsonRequestMixin
from core.Mixin.StatusWrapMixin import StatusWrapMixin
from core.dss.Mixin import CheckTokenMixin, FormJsonResponseMixin
from event.forms import AdEventForm


class CreateAdEventView(CheckTokenMixin, StatusWrapMixin, JsonRequestMixin, FormJsonResponseMixin, CreateView):
    form_class = AdEventForm
    http_method_names = ['post']
    conf = {}

    def form_valid(self, form):
        try:
            super(CreateAdEventView, self).form_valid(form)
            event = form.save()
            event.user_id = self.user.id
            event.save()
            return self.render_to_response(dict())
        except Exception as e:
            return self.render_to_response(extra={'error': e.message})
