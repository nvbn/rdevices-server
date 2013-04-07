from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from devices.models import Device, DeviceMethod
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
                'a': 'str',
                'b': 'str',
            },
            'name': 'method',
            'description': 'description',
            'action': 'declare',
        }
        self.sock.send(json.dumps(self.declaration) + '\n')
        self._declare_out = self.server.stdout.readline()

    def _parse(self, out):
        """Parse output"""
        method, data = self._declare_out.split(':', 1)
        obj = json.loads(data.strip())
        return method, obj

    def test_declare_methods(self):
        """Test method declaration"""
        method, call = self._parse(self._declare_out)
        self.assertEqual(method, 'Declare')
        self.assertDictEqual(
            call['spec'], self.declaration['spec'],
        )
        self.assertEqual(call['device'], self.declaration['uuid'])

