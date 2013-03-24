$ ->
    $('.devices').imagesLoaded ->
        $('.devices').masonry
            itemSelector: '.device-box'

    prettyPrint()

    if $('.create-new-device-form').length
        view = new DeviceFormView()
        view.setElement $('.device-form')
        view.delegateEvents()
