$ ->
    $('.devices').imagesLoaded ->
        $('.devices').masonry
            itemSelector: '.device-box'

    $('.dashboards').imagesLoaded ->
        $('.dashboards').masonry
            itemSelector: '.dashboard-box'

    prettyPrint()

    if $('.device-form').length
        view = new DeviceFormView()
        view.setElement $('.device-form')
        view.delegateEvents()

    $('[data-toggle=tooltip]').tooltip()

    $('.submit-form').click (e) ->
        e.preventDefault()
        $(e.currentTarget).closest('form').submit()
        false

    $('.copy-it').click (e) ->
        e.preventDefault()
        false

    if $('#editor-holder').length
        model = new Dashboard
            id: window.dashboardId
        model.fetch
            success: (model) ->
                view = new ChangeDashboardView
                    model: model
                view.setElement $('#editor-holder')
                view.render()

    _.each $('.requests-holder'), (holder) ->
        $holder = $(holder)
        view = new MethodCallsView
        view.setMethod $holder.data('method')
        view.setElement $holder
        view.render()

    _.each $('.device-status-icon'), (icon) ->
        device = $(icon).data 'device'
        call = new DeviceMethodCall
        call.save
            device: device
            method: 'is_online'
            request: {}
        ,
            success: =>
                calls = 0
                checkCall = =>
                    call.fetch
                        success: (call) =>
                            if call.get('state')
                                $(icon).removeClass 'offline'
                                $(icon).addClass 'online'
                            else if calls < 5
                                calls += 1
                                setTimeout checkCall, 1000
                checkCall()

    $('.show-code-block').click (e) ->
        e.preventDefault()
        target = $(e.currentTarget)
        $('.show-code-block').removeClass 'active-block'
        target.addClass 'active-block'
        $('.code-block').css 'display', 'none'
        $('.code-block.' + target.data('block')).css 'display', 'block'
