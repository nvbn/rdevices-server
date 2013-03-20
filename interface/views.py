from annoying.decorators import render_to


@render_to('site/index.html')
def index(request):
    """Index page"""
    return {}


@render_to('site/devices.html')
def devices(request):
    """Devices page"""
    return {}
