from tornado.netutil import TCPServer
from devices.models import DeviceMethodCall, Device, DeviceMethod
import json


class DeviceConnection(object):
    """Device connection"""

    def __init__(self, stream):
        """Init callback and start reading"""
        self._stream = stream
        self._stream.set_close_callback(self._on_close)
        self._read()

    def _read(self):
        """Start reading"""
        self._stream.read_until('\n', self._on_receive)

    def _on_close(self, *args, **kwargs):
        pass

    def _on_receive(self, data):
        """Process data and continue reading"""
        self._process_data(data)
        self._read()

    def _process_data(self, data):
        """Process data and run handler"""
        try:
            request = json.loads(data[:-1])
            action = request['action']
            if action == 'declare':
                self.action_declare(request)
            elif action == 'response':
                self.action_response(request)
        except Exception as e:
            # fail silently
            print e

    def action_declare(self, data):
        """Create new method or update exist"""
        device = Device.objects.get(
            uuid=data['uuid'],
        )
        method, created = DeviceMethod.objects.get_or_create(
            device=device,
            name=data['name'],
        )
        method.spec = data['spec']
        method.description = data['description']
        method.save()

    def action_response(self, data):
        """Set response to method call"""
        call = DeviceMethodCall.objects.get(
            id=data['request_id'],
            method__device__uuid=data['uuid'],
            state=DeviceMethodCall.STATE_CREATED
        )
        call.response = data['response']
        call.state = DeviceMethodCall.STATE_FINISHED
        call.save()


class DeviceServer(TCPServer):
    """Server for device connections"""

    def handle_stream(self, stream, address):
        """Create device connection for stream"""
        DeviceConnection(stream)
