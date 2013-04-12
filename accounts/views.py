from django.shortcuts import redirect
from django.views.generic import (
    ListView, DeleteView, View,
)
from django.core.urlresolvers import reverse
from accounts.models import ApiKey
from tools.mixins import LoginRequiredMixin


class ApiKeyMixin(object):
    """Mixin for api keys"""
    model = ApiKey

    def get_queryset(self):
        """Get user api keys"""
        return ApiKey.objects.filter(user=self.request.user)


class ApiKeyList(LoginRequiredMixin, ApiKeyMixin, ListView):
    """List api keys view"""
    template_name = 'accounts/apikeys_list.html'
    context_object_name = 'keys'


class ApiKeyCreate(LoginRequiredMixin, ApiKeyMixin, View):
    """Create new api key view"""

    def post(self, *args, **kwargs):
        """Create api key for user"""
        self._create_apikey()
        return redirect(
            reverse('accounts_keys_list', kwargs={
                'username': self.request.user.username,
            }),
        )

    def _create_apikey(self):
        """Create api key"""
        ApiKey.objects.create(
            user=self.request.user,
        )


class ApiKeyDelete(LoginRequiredMixin, ApiKeyMixin, DeleteView):
    """Delete api key"""
    template_name = 'accounts/apikeys_delete.html'
    slug_field = 'key'
    context_object_name = 'key'

    def get_success_url(self):
        """Get redirect url"""
        return reverse('accounts_keys_list', kwargs={
            'username': self.request.user.username,
        })
