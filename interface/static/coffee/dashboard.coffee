STATE_FINISHED = 1

class window.DeviceHelper
    constructor: (@model) -> @

    loadMethods: (callback) ->
        @model.fetchRelated 'methods',
            success: (method) =>
                @[method.get('name')] = (request, requestCallback) =>
                    @callMethod method, request, requestCallback
            setTimeout (=>callback.call @), 0

    callMethod: (method, request, callback) ->
        call = new DeviceMethodCall
            method: method.id
            request: request
        call.save()
        @checkCall call, =>
            if callback
                callback.call call

    checkCall: (call, callback) ->
        call.fetch
            success: (call) =>
                if call.get('state') == STATE_FINISHED
                    callback.call call.get('response')
                else
                    setTimeout =>
                        @checkCall call, callback
                    , 1



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
