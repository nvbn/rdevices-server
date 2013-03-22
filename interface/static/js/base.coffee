$ ->
    $('.devices').imagesLoaded ->
        $('.devices').masonry
            itemSelector: '.device-box'
            columnWidth: 300
