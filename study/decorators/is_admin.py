from functools import wraps
from django.http import HttpResponseForbidden


def admin_only(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):

        profile = request.user.profile
        if profile.type == 1:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden('No permission')

    return wrap
