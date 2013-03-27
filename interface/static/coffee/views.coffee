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


class window.ChangeDashboardView extends Backbone.View
    element: 'div'
    templateId: '#editor-tmpl'
    events:
        'click .save': 'save'

    constructor: (options) ->
        super options
        @loadTemplates()

    loadTemplates: ->
        @template = _.template $(@templateId).html()

    render: ->
        @$el.html @template @model.attributes
        @createEditor()
        @initEvents()

    createEditor: ->
        @editor = ace.edit "editor"
        @editor.setTheme "ace/theme/textmate"
        @editor.getSession().setMode "ace/mode/html"

    initEvents: ->
        @$el.find('a[data-toggle="tab"]').on 'shown', (e) =>
            tab = $($(e.target).attr 'href')
            if tab.attr('id') == 'preview-tab'
                @showPreview()
            true

    showPreview: ->
        @$el.find('#editor-preview').contents().find('body').html @editor.getSession().getValue()

    save: (e) ->
        e.preventDefault()
        @model.set 'code', @editor.getSession().getValue()
        @model.save()
        @model.fetch
            success: ->
                document.location = window.absoluteUrl;
        false
