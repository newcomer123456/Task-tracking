from django.core.exceptions import PermissionDenied


class UserIsOwnerMixin(object):
    def dispatch(self, request, *args, **kwargs):
        instansce = self.get_object()


