$ ->
    $('.devices').imagesLoaded ->
        $('.devices').masonry
            itemSelector: '.device-box'

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
