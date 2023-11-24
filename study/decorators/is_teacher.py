from functools import wraps
from django.http import HttpResponseForbidden


def teacher_only(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):

        profile = request.user.profile
        if profile.type == 2:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden('No permission')

    return wrap
