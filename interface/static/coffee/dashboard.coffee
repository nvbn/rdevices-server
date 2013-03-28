STATE_FINISHED = 1


class window.DeviceHelper
    constructor: (@model) -> @

    loadMethods: (callback) ->
        methodsWhen = @model.fetchRelated('methods')
        needMethods = methodsWhen.length
        _.each methodsWhen, (methodWhen) =>
            methodWhen.then (method) =>
                @[method.name] = (request, options) =>
                    @callMethod method, request, options
                @[method.name].getCalls = (options) =>
                    @getMethodCalls method, options
                needMethods -= 1
                if not needMethods
                    callback.call @, 0

    callMethod: (method, request, options) ->
        if _.isFunction options
            callback = options
        else if options
            callback = options.success or (->@)
        else
            callback = (->@)
        call = new DeviceMethodCall
        call.save
            method: method.resource_uri
            request: request
        ,
            success: =>
                @checkCall call, =>
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

    getMethodCalls: (method, options) ->
        if not options.data
            options.data = {}
        options.data.method = method.id
        DeviceMethodCallCollection.fetch options


class window.DashboardHelper
    constructor: (@id) ->
        @called = false
        @devices = {}

    ready: (callback) ->
        if @called
            callback.call()
        else
            @called = true
            $ =>
                @loadDashboard =>
                    callback.call @

    loadDashboard: (callback) ->
        @model = new Dashboard
            id: @id
        @model.fetch
            success:(model) =>
                @model = model
                callback.call @

    getDevice: (deviceId, options) ->
        if _.isFunction options
            callback = options
        else
            callback = options.success or (->@)
        if @devices[deviceId]
            callback.call @, @devices[deviceId]
        else
            device = new Device
                id: deviceId
            device.fetch
                success: (device) =>
                    helper = new DeviceHelper device
                    helper.loadMethods =>
                        @devices[deviceId] = helper
                        callback.call @, helper
