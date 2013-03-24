class window.Device extends Backbone.RelationalModel
    urlRoot: '/api/v1/device/'
    relations: [
            type: Backbone.HasMany
            key: 'methods'
            relatedModel: 'DeviceMethod'
            collectionType: 'DeviceMethodCollection'
            reverseRelation:
                key: 'device'
    ]


class window.DeviceCollection extends Backbone.Collection
    url: '/api/v1/device/'
    model: Device


class window.DeviceMethod extends Backbone.RelationalModel
    urlRoot: '/api/v1/device_method/'
    relations: [
            type: Backbone.HasMany
            key: 'calls'
            relatedModel: 'DeviceMethodCall'
            collectionType: 'DeviceMethodCallCollection'
            reverseRelation:
                key: 'method'
    ]


class window.DeviceMethodCollection extends Backbone.Collection
    url: '/api/v1/device_method/'
    model: DeviceMethod


class window.DeviceMethodCall extends Backbone.RelationalModel
    urlRoot: '/api/v1/device_method_call/'


class window.DeviceMethodCallCollection extends Backbone.Collection
    url: '/api/v1/device_method_call/'
    model: DeviceMethodCall
