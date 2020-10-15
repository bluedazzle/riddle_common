# coding: utf-8
from account.models import User


class ABTestMiddleWare(object):
    def get_ab_test_config(self):
        pass

    def get_ab_test_id(self, user_id):
        pass

    def get_destroy_ab_test_list(self):
        pass

    def process_request(self, request):
        token = request.GET.get('token', None) or request.POST.get('token', None)
        user = None
        if not token:
            token = request.session.get('token', '')
        if token:
            user_list = User.objects.filter(token=token)
            if user_list.exists():
                user = user_list[0]
        setattr(request, 'user', user)
        if user:
            if not user.ab_test_id:
                ab_test_id = self.get_ab_test_id(user.id)
                if ab_test_id:
                    user.ab_test_id = ab_test_id
                    user.save()
            else:
                ban_list = self.get_destroy_ab_test_list()
                group_id, test_id = user.ab_test_id.split('AB')
                if group_id in ban_list:
                    ab_test_id = self.get_ab_test_id(user.id)
                    if ab_test_id:
                        user.ab_test_id = ab_test_id
                        user.save()
