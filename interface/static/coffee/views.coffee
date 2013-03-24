class window.DeviceFormView extends Backbone.View
    element: 'form'
    previewHolder: '.preview-holder'
    previewTemplateId: '#preview-tmpl'
    events:
        'change #id_image': 'previewImage'

    constructor: (options) ->
        super options
        @loadTemplates()

    loadTemplates: ->
        @previewTemplate = _.template $(@previewTemplateId).html()

    previewImage: (e) ->
        files = e.currentTarget.files
        if files and files[0] and files[0].type.search('image/') == 0
            reader = new FileReader
            $(reader).load (e) =>
                uri = e.target.result
                @$el.find(@previewHolder).html @previewTemplate
                    uri: uri
            reader.readAsDataURL files[0]
