from tornado.netutil import TCPServer
import tornadoredis
from devices.models import DeviceMethodCall, Device, DeviceMethod
from functools import partial
import tornado.gen
import json


class DeviceConnection(object):
    """Device connection"""

    def __init__(self, stream, server):
        """Init callback and start reading"""
        self._stream = stream
        self._server = server
        self.uuid = None
        self._stream.set_close_callback(
            partial(server.unregister, self.uuid),
        )
        self._read()

    def _read(self):
        """Start reading"""
        self._stream.read_until('\n', self._on_receive)

    def _on_receive(self, data):
        """Process data and continue reading"""
        self._process_data(data)
        self._read()

    def _set_uuid(self, uuid):
        """Set uuid and register"""
        if not self.uuid:
            self.uuid = uuid
            self._server.register(uuid, self)

    def _process_data(self, data):
        """Process data and run handler"""
        try:
            request = json.loads(data[:-1])
            action = request['action']
            self._set_uuid(request['uuid'])
            if action == 'declare':
                self.action_declare(request)
            elif action == 'response':
                self.action_response(request)
        except Exception as e:
            # fail silently
            print e

    def action_declare(self, request):
        """Create new method or update exist"""
        device = Device.objects.get(
            uuid=request['uuid'],
        )
        method, created = DeviceMethod.objects.get_or_create(
            device=device,
            name=request['name'],
        )
        method.spec = request['spec']
        method.description = request['description']
        method.save()

    def action_response(self, request):
        """Set response to method call"""
        call = DeviceMethodCall.objects.get(
            id=request['request_id'],
            method__device__uuid=request['uuid'],
            state=DeviceMethodCall.STATE_CREATED
        )
        call.response = request['response']
        call.state = DeviceMethodCall.STATE_FINISHED
        call.save()

    def send_request(self, request):
        """Send request to device"""
        self._stream.write(json.dumps(request) + '\n')


class DeviceServer(TCPServer):
    """Server for device connections"""

    def __init__(self, calls_channel, *args, **kwargs):
        self._connections = {}
        self._calls_channel = calls_channel
        self._init_channel()
        super(DeviceServer, self).__init__(*args, **kwargs)

    @tornado.gen.engine
    def _init_channel(self):
        """Init channel and start consumption"""
        self._r = tornadoredis.Client()
        self._r.connect()
        yield tornado.gen.Task(
            self._r.subscribe, self._calls_channel,
        )
        self._r.listen(self._on_call)

    def _on_call(self, msg):
        """On new call"""
        try:
            data = json.loads(msg.body)
            self._connections[data['uuid']].send_request(
                data,
            )
        except Exception as e:
            # fail silently
            print e
            pass

    def handle_stream(self, stream, address):
        """Create device connection for stream"""
        DeviceConnection(stream, self)

    def register(self, uuid, connection):
        """Register connection"""
        self._connections[uuid] = connection
        print self._connections

    def unregister(self, uuid):
        """Unregister connection"""
        if uuid in self._connections:
            self._connections.pop(uuid)
