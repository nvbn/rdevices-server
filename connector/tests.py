from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from devices.models import Device, DeviceMethodCall, DeviceMethod
from tools.shortcuts import send_call_request
from tools import connections
import subprocess
import socket
import time
import json
import os


class RequestsCase(TestCase):
    """Test requests"""
    fixtures = ['connector/fixtures/test_data.json']

    def setUp(self):
        """Create server and initial data"""
        try:
            os.unlink(os.path.join(
                settings.PROJECT_ROOT, settings.TEST_DAEMON_DB,
            ))
        except OSError:
            pass
        subprocess.call([
            'python', 'manage.py', 'syncdb', '--noinput',
            '--settings=rdevices.test_daemons_settings',
        ], stdout=subprocess.PIPE)
        subprocess.call([
            'python', 'manage.py', 'migrate', '--noinput',
            '--settings=rdevices.test_daemons_settings',
        ], stdout=subprocess.PIPE)
        subprocess.call([
            'python', 'manage.py', 'loaddata', 'connector/fixtures/test_data.json',
            '--settings=rdevices.test_daemons_settings',
        ], stdout=subprocess.PIPE)
        self.server = subprocess.Popen([
            'python', 'manage.py', 'run_connector', settings.TEST_CONNECTOR,
            '--settings=rdevices.test_daemons_settings',
        ], stdout=subprocess.PIPE)
        self._connect()
        self.user = User.objects.get(pk=1)
        self.device = Device.objects.get(pk=1)
        self.method = DeviceMethod.objects.get(pk=1)
        self.call = DeviceMethodCall.objects.get(pk=1)
        self._declare()

    def tearDown(self):
        """Terminate server"""
        self.server.terminate()

    def _connect(self):
        """Connect to server"""
        while True:
            host, port = settings.TEST_CONNECTOR.split(':')
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM,
            )
            try:
                self.sock.connect((host, int(port)))
                break
            except socket.error:
                time.sleep(1)

    def _declare(self):
        """Declare method"""
        self.declaration = {
            'uuid': self.device.uuid,
            'spec': {
                'x': 'str',
                'y': 'str',
            },
            'name': 'method',
            'description': 'description',
            'action': 'declare',
        }
        self.sock.send(json.dumps(self.declaration) + '\n')
        self._declare_out = self.server.stdout.readline()

    def _request(self):
        """Send request"""
        self._request_id = 2
        send_call_request(
            action='request',
            method=self.declaration['name'],
            request_id=self._request_id,
            uuid=self.declaration['uuid'],
            request={
                'x': 'valA',
                'y': 'valB',
            },
        )
        self._request_out = self.server.stdout.readline()

    def _parse(self, out):
        """Parse output"""
        method, data = out.split(':', 1)
        obj = json.loads(data.strip())
        return method, obj

    def _read(self):
        """Read from sock before new line"""
        out = ''
        while True:
            char = self.sock.recv(1)
            if char == '\n':
                return out
            else:
                out += char

    def test_declare_methods(self):
        """Test method declaration"""
        method, call = self._parse(self._declare_out)
        self.assertEqual(method, 'Declare')
        self.assertDictEqual(
            call['spec'], self.declaration['spec'],
        )
        self.assertEqual(call['device'], self.declaration['uuid'])

    def test_method_request(self):
        """Test method requests"""
        self._request()
        method, data = self._parse(self._request_out)
        self.assertEqual(method, 'Request')
        self.assertEqual(data['request_id'], self._request_id)
        request = json.loads(self._read())
        self.assertEqual(request['action'], 'request')
        self.assertEqual(request['uuid'], self.declaration['uuid'])
        self.assertEqual(request['request_id'], self._request_id)

    def test_method_response(self):
        """Test method response"""
        pubsub = connections.r.pubsub()
        pubsub.subscribe(settings.NOTIFICATIONS_CHANNEL)
        next(pubsub.listen())
        send_call_request(
            action='request',
            method=self.method.name,
            request_id=self.call.id,
            uuid=self.device.uuid,
            request={
                'x': 'valA',
                'y': 'valB',
            },
        )
        self.server.stdout.readline()
        request = json.loads(self._read())
        response_value = 'response'
        self.sock.send(json.dumps({
            'request_id': self.call.id,
            'uuid': self.device.uuid,
            'action': 'response',
            'response': response_value,
        }) + '\n')
        out = self.server.stdout.readline()
        method, data = self._parse(out)
        self.assertEqual(method, 'Response')
        self.assertEqual(data['response'], response_value)
        self.assertEqual(data['request_id'], request['request_id'])
        msg = next(pubsub.listen())
        notify = json.loads(msg['data'])
        self.assertEqual(notify['action'], 'call_changed')
        self.assertEqual(notify['user_id'], self.user.id)
        self.assertEqual(notify['call_id'], self.call.id)
