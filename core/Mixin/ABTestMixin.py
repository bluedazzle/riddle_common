# coding: utf-8
import logging

from baseconf.models import ABTest
from core.consts import STATUS_DESTROY, STATUS_ENABLE


class ABTestMixin(object):
    ab_start_value = 0
    ab_end_value = 0
    ab_a = None
    ab_b = None
    ab_status = STATUS_DESTROY
    ab_slug = ''

    def get_ab_conf(self, group_id, test_id):
        test_id = int(test_id)
        objs = ABTest.objects.filter(id=group_id).all()
        if not objs.exists():
            return False
        obj = objs[0]
        self.ab_status = obj.status
        self.ab_slug = obj.slug
        if test_id == 1:
            self.ab_a = True
            self.ab_b = False
            self.ab_start_value = obj.test_a_start_value
            self.ab_end_value = obj.test_a_end_value
        if test_id == 2:
            self.ab_a = False
            self.ab_b = True
            self.ab_start_value = obj.test_b_start_value
            self.ab_end_value = obj.test_b_end_value
        return obj

    def handler_default(self, *args, **kwargs):
        pass

    def handler_b(self, *args, **kwargs):
        pass

    def ab_test_handle(self, slug, *args, **kwargs):
        if slug != self.ab_slug:
            return self.handler_default(*args, **kwargs)
        if self.ab_status != STATUS_ENABLE:
            return self.handler_default(*args, **kwargs)
        if self.ab_a:
            return self.handler_default(*args, **kwargs)
        if self.ab_b:
            return self.handler_b(*args, **kwargs)
        return None

    def dispatch(self, request, *args, **kwargs):
        ab_test_id = str(request.account.ab_test_id)
        ab_test_id = ab_test_id.upper().strip()
        if ab_test_id:
            try:
                group_id, test_id = ab_test_id.split('AB')
                self.get_ab_conf(group_id, test_id)
            except Exception as e:
                logging.exception(e)
        return super(ABTestMixin, self).dispatch(request, *args, **kwargs)
