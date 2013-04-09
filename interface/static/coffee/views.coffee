class window.LazyTemplatedView extends Backbone.View
    constructor: (options) ->
        super options
        @loadTemplates()

    loadTemplates: ->
        @template = _.template $(@templateId).html()


class window.DeviceFormView extends Backbone.View
    tagName: 'form'
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


class window.ChangeDashboardView extends LazyTemplatedView
    tagName: 'div'
    templateId: '#editor-tmpl'
    events:
        'click .save': 'save'

    render: ->
        @$el.html @template @model.attributes
        @createEditor()
        @initEvents()

    createEditor: ->
        @editor = ace.edit "editor"
        @editor.setTheme "ace/theme/textmate"
        @editor.getSession().setMode "ace/mode/html"
        @editor.getSession().setValue @model.get('code')

    initEvents: ->
        @$el.find('a[data-toggle="tab"]').on 'shown', (e) =>
            tab = $($(e.target).attr 'href')
            if tab.attr('id') == 'preview-tab'
                @showPreview()
            true
        $('button.save').tooltip
            trigger: 'manual'
            placement: 'right'

    showPreview: ->
        @model.save
            preview: @editor.getSession().getValue()
        ,
            success: =>
                preview = @$el.find('#editor-preview')[0]
                preview.contentWindow.location.reload()

    save: (e) ->
        e.preventDefault()
        @model.save
            code: @editor.getSession().getValue()
        ,
            patch: true
        $(e.currentTarget).tooltip('show')
        setTimeout (=>$(e.currentTarget).tooltip('hide')), 3000
        false


class window.MethodCallsView extends LazyTemplatedView
    tagName: 'div'
    templateId: '#device-method-calls-tmpl'
    limit: 20
    offset: 0
    events:
        'click .show-more': 'more'

    setMethod: (@methodId) -> @

    render: ->
        collection = new DeviceMethodCallCollection
        collection.fetch
            data:
                method_id: @methodId
                limit: @limit
                offset: @offset
                with_pretty: true
            success: (collection) =>
                if collection.meta.total_count > (@offset + @limit)
                    @$el.find('.show-more').css 'display', 'block'
                else
                    @$el.find('.show-more').css 'display', 'none'
                collection.each (item) =>
                    @$el.find('ul').append @template item.attributes

    more: (e) ->
        e.preventDefault()
        @offset += @limit
        @render()
        false
