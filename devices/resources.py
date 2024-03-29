from devices.models import (
    Device, DeviceMethod, DeviceMethodCall, Dashboard,
)
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization, Unauthorized
from tastypie.authentication import MultiAuthentication, Authentication
from tastypie.exceptions import BadRequest
from tastypie import fields
from accounts.authentication import ManyApiKeyAuthentication


class DeviceAuthorization(DjangoAuthorization):
    """Authorization for device"""

    def read_list(self, object_list, bundle):
        """Return only owner devices"""
        return super(DeviceAuthorization, self).read_list(
            object_list.filter(owner=bundle.request.user), bundle,
        )

    def read_detail(self, object_list, bundle):
        """Return only owner device"""
        if bundle.obj.owner == bundle.request.user:
            return super(DeviceAuthorization, self).read_detail(
                object_list, bundle,
            )
        else:
            raise Unauthorized('Not your device')


class DeviceResource(ModelResource):
    """Resource for devices"""
    methods = fields.ToManyField(
        'devices.resources.DeviceMethodResource', 'methods',
        blank=True, full=False,
    )

    class Meta:
        queryset = Device.objects.select_related('methods')
        resource_name = 'device'
        allowed_methods = ('get',)
        authorization = DeviceAuthorization()
        authentication = MultiAuthentication(
            ManyApiKeyAuthentication(), Authentication(),
        )
        excludes = ('owner',)


class DeviceMethodAuthorization(DjangoAuthorization):
    """Authorization for device methods"""

    def read_list(self, object_list, bundle):
        """Return only owner methods"""
        return super(DeviceMethodAuthorization, self).read_list(
            object_list.filter(device__owner=bundle.request.user), bundle,
        )

    def read_detail(self, object_list, bundle):
        """Return only owner method"""
        if bundle.obj.device.owner == bundle.request.user:
            return super(DeviceMethodAuthorization, self).read_detail(
                object_list, bundle,
            )
        else:
            raise Unauthorized('Not your device method')


class DeviceMethodResource(ModelResource):
    """Resource for device methods"""
    device = fields.ToOneField(DeviceResource, 'device')

    class Meta:
        queryset = DeviceMethod.objects.select_related('device')
        resource_name = 'device_method'
        authorization = DeviceMethodAuthorization()
        authentication = MultiAuthentication(
            ManyApiKeyAuthentication(), Authentication(),
        )
        allowed_methods = ('get',)


class DeviceMethodCallAuthorization(DjangoAuthorization):
    """Authorization for device method call"""

    def read_list(self, object_list, bundle):
        """Return only owner devices"""
        return super(DeviceMethodCallAuthorization, self).read_list(
            object_list.filter(caller=bundle.request.user), bundle,
        )

    def read_detail(self, object_list, bundle):
        """Return only owner device"""
        if bundle.obj.caller == bundle.request.user:
            return super(DeviceMethodCallAuthorization, self).read_detail(
                object_list, bundle,
            )
        else:
            raise Unauthorized('Not your call')

    def create_detail(self, object_list, bundle):
        """Check method owner"""
        return True

    def update_detail(self, object_list, bundle):
        """Updates not allowed"""
        raise Unauthorized('Updates not allowed')

    def delete_detail(self, object_list, bundle):
        """Deletes not allowed"""
        raise Unauthorized('Deletes not allowed')


class DeviceMethodCallResource(ModelResource):
    """Resource for device method calls"""

    def build_filters(self, filters=None, request=None):
        applicable_filters = super(
            DeviceMethodCallResource, self,
        ).build_filters(filters)
        if filters.get('method_id') and\
                DeviceMethod.objects.filter(
                    id=filters['method_id'],
                    device__owner=request.user,
                ).count():
            applicable_filters['method__id'] = filters['method_id']
        return applicable_filters

    def obj_get_list(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_get_list``.

        Takes an optional ``request`` object, whose ``GET`` dictionary can be
        used to narrow the query.
        """
        filters = {}

        if hasattr(bundle.request, 'GET'):
            # Grab a mutable copy.
            filters = bundle.request.GET.copy()

        # Update with the provided kwargs.
        filters.update(kwargs)
        applicable_filters = self.build_filters(
            filters=filters, request=bundle.request,
        )

        try:
            objects = self.apply_filters(bundle.request, applicable_filters)
            return self.authorized_read_list(objects, bundle)
        except ValueError:
            raise BadRequest(
                "Invalid resource lookup data provided (mismatched type).",
            )

    def obj_create(self, bundle, **kwargs):
        """Create call with caller"""
        # very hackish, but greater improve performance
        try:
            bundle.obj = DeviceMethodCall.objects.create(
                caller=bundle.request.user,
                method=DeviceMethod.objects.get(
                    name=bundle.data['method'],
                    device__uuid=bundle.data['device'],
                    device__owner=bundle.request.user,
                ),
                request=bundle.data['request'],
            )
            return bundle
        except (DeviceMethod.DoesNotExist, KeyError):
            self.unauthorized_result('Not allowed method')

    def dehydrate(self, bundle):
        """Add pretty field to bundle"""
        bundle.data['text_state'] = bundle.obj.get_state()
        bundle.data['method_id'] = bundle.obj.method.id
        if bundle.request.GET.get('with_pretty'):
            bundle.data['pretty_request'] = bundle.obj.pretty_request()
            bundle.data['pretty_response'] = bundle.obj.pretty_response()
        return bundle

    class Meta:
        queryset = DeviceMethodCall.objects.all()
        resource_name = 'device_method_call'
        authorization = DeviceMethodCallAuthorization()
        authentication = MultiAuthentication(
            ManyApiKeyAuthentication(), Authentication(),
        )
        always_return_data = True
        list_allowed_methods = ('get', 'post',)
        detailed_allowed_methods = ('get',)
        excludes = ('caller', 'method')


class DashboardAuthorization(DjangoAuthorization):
    """Authorization for dashboards"""

    def read_list(self, object_list, bundle):
        """Return only owner devices"""
        return super(DashboardAuthorization, self).read_list(
            object_list.filter(owner=bundle.request.user), bundle,
        )

    def read_detail(self, object_list, bundle):
        """Return only owner device"""
        if bundle.obj.owner == bundle.request.user:
            return super(DashboardAuthorization, self).read_detail(
                object_list, bundle,
            )
        else:
            raise Unauthorized('Not your dashboard')

    def create_detail(self, object_list, bundle):
        """Check method owner"""
        return True

    def update_detail(self, object_list, bundle):
        """Update only owner dashboards"""
        if bundle.obj.owner == bundle.request.user:
            return True
        else:
            raise Unauthorized('Not your dashboard')

    def delete_detail(self, object_list, bundle):
        """Update only owner dashboards"""
        if bundle.obj.owner == bundle.request.user:
            return True
        else:
            raise Unauthorized('Not your dashboard')


class DashboardResource(ModelResource):
    """Resource for dashboards"""

    def obj_create(self, bundle, **kwargs):
        """Create call with caller"""
        return super(DashboardResource, self).obj_create(
            bundle, owner=bundle.request.user, **kwargs
        )

    class Meta:
        queryset = Dashboard.objects.all()
        resource_name = 'dashboard'
        authorization = DashboardAuthorization()
        authentication = MultiAuthentication(
            ManyApiKeyAuthentication(), Authentication(),
        )
        allowed_methods = ('get', 'post', 'put', 'delete', 'patch')
        excludes = ('slug', 'owner', 'image')
