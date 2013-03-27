STATE_FINISHED = 1

class window.DeviceHelper
    constructor: (@model) -> @

    loadMethods: (callback) ->
        methodsWhen = @model.fetchRelated('methods')
        needMethods = methodsWhen.length
        _.each methodsWhen, (methodWhen) =>
            methodWhen.then (method) =>
                @[method.name] = (request, requestCallback) =>
                    @callMethod method, request, requestCallback
                needMethods -= 1
                if not needMethods
                    callback.call @, 0

    callMethod: (method, request, callback) ->
        call = new DeviceMethodCall
            method: method.resource_uri
            request: request
        call.save()
        @checkCall call, =>
            if callback
                callback.call @, call.get('response')

    checkCall: (call, callback) ->
        call.fetch
            success: (call) =>
                if call.get('state') == STATE_FINISHED
                    callback.call call.get('response')
                else
                    setTimeout =>
                        @checkCall call, callback
                    , 1000



class window.DashboardHelper
    constructor: (@id) ->
        @called = false

    ready: (callback) ->
        if @called
            callback.call()
        else
            @called = true
            $ =>
                @loadDashboard =>
                    @loadDevice =>
                        callback.call @

    loadDashboard: (callback) ->
        @model = new Dashboard
            id: @id
        @model.fetch
            success:(model) =>
                @model = model
                callback.call @

    loadDevice: (callback) ->
        @model.fetchRelated 'device',
            success: (device) =>
                @device = new DeviceHelper device
                @device.loadMethods =>
                    callback.call @
