from django.conf import settings
import os
import subprocess


class TestWithDaemonMixin(object):
    """Mixin for tests with daemons"""
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
