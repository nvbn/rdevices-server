from django.test import TestCase
from django.conf import settings
from tools.tests import TestWithDaemonMixin
from tools import connections
import subprocess
import json


class RequestsCase(TestCase, TestWithDaemonMixin):
    """Test requests"""

    def setUp(self):
        """Create server and initial data"""
        TestWithDaemonMixin.setUp(self)
        self.server = subprocess.Popen([
            'python', 'manage.py', 'run_push', settings.TEST_PUSH,
            '--settings=rdevices.test_daemons_settings',
        ], stdout=subprocess.PIPE)

    def tearDown(self):
        """Terminate server"""
        self.server.terminate()

    def test_start(self):
        """Test start consuming"""
        out = self.server.stdout.readline()
        self.assertEqual(
            out.strip(), 'Start consuming',
        )

    def test_receive(self):
        """Test receive messages from redis"""
        self.server.stdout.readline()
        user_id = 12
        message = 'message'
        connections.r.publish(
            settings.NOTIFICATIONS_CHANNEL,
            json.dumps({
                'user_id': user_id,
                'message': message,
            }),
        )
        method, data = self.server.stdout.readline().split(':', 1)
        request = json.loads(data.strip())
        self.assertEqual(method, 'Call')
        self.assertEqual(request['user_id'], user_id)
        self.assertEqual(request['message'], message)
