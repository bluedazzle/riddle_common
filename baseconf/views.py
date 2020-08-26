# coding: utf-8
from __future__ import unicode_literals

# Create your views here.
from django.views.generic import DetailView

from core.Mixin.StatusWrapMixin import StatusWrapMixin
from core.dss.Mixin import MultipleJsonResponseMixin
from baseconf.models import GlobalConf
from core.utils import get_global_conf


class GlobalConfView(StatusWrapMixin, MultipleJsonResponseMixin, DetailView):
    model = GlobalConf
    slug_field = 'token'

    # exclude_attr = ['']

    def get(self, request, *args, **kwargs):
        conf = get_global_conf()
        return self.render_to_response(conf)
