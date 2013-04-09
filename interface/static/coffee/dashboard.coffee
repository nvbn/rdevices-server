STATE_FINISHED = 1


class window.NotificationsHelper
    constructor: (callback) ->
        _.extend @, Backbone.Events

        @openConnection callback
        @initEvents()

    openConnection: (callback) ->
        alreadyOpened = false
        window.sock.onopen = =>
            if not alreadyOpened
                alreadyOpened = true
                callback.call @
            window.sock.send JSON.stringify
                action: 'subscribe'
                user_id: window.userId

    initEvents: ->
        window.sock.onmessage = (message) =>
            if message.data.action == 'call_changed'
                @trigger 'callChanged_' + message.data.call_id


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
        window.dashboard.calls.push =>
            if _.isFunction options
                callback = options
            else if options
                callback = options.success or (->@)
            else
                callback = (->@)
            call = new DeviceMethodCall
            call.save
                method_id: method.id
                request: request
            ,
                success: =>
                    @checkCall call, =>
                        callback.call @, call.get('response')

    checkCall: (call, callback) ->
        window.dashboard.notifications.on 'callChanged_' + call.get('id'), =>
            call.fetch
                success: (call) =>
                    callback.call call.get('response')

    getMethodCalls: (method, options) ->
        if not options.data
            options.data = {}
        options.data.method = method.id
        DeviceMethodCallCollection.fetch options


class window.DashboardHelper
    constructor: (@id) ->
        @called = false
        @devices = {}
        @waiters = []
        @calls = []

    _ready: (callback) ->
        $ =>
            @initPush =>
                @loadDashboard =>
                    @called = true
                    callback.call @
                    _.each @waiters, (waiter) =>
                        waiter.call @
                    @runCalls()

    ready: (callback) ->
        if @called
            callback.call @
        else
            @waiters.push callback

    initPush: (callback) ->
        @notifications = new NotificationsHelper callback

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

    runCalls: ->
        call = @calls.shift()
        if call
            call.call @
        setTimeout (=>@runCalls()), 500

$ ->
    window.dashboard._ready ->
        if $('[type="text/coffeescript"]').length
            $.getScript window.staticRoot + 'js/coffee-script.js', ->
                _.each $('[type="text/coffeescript"]'), (script) ->
                    CoffeeScript.run $(script).html()

        if $('[type="text/iced-coffeescript"]').length
            $.getScript window.staticRoot + 'js/coffee-script-iced.js', ->
                _.each $('[type="text/iced-coffeescript"]'), (script) ->
                    CoffeeScript.run $(script).html()
