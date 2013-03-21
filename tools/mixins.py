from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    """Login required mixin"""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """Only for authorised users"""
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
