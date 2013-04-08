from django.conf import settings
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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


class SeleniumTestMixin(object):
    """Mixin for selenium tests"""

    def setUp(self):
        """Create items"""
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = self.live_server_url
        self.verificationErrors = []
        self.accept_next_alert = True
        self.user = User.objects.create(
            username='test_user',
            email='test_user@test.test',
            is_active=True,
        )
        self.user.set_password('test')
        self.user.save()

    def _login(self):
        """Login"""
        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_link_text("sign in").click()
        driver.find_element_by_id("id_identification").clear()
        driver.find_element_by_id("id_identification").send_keys("test_user")
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys("test")
        driver.find_element_by_css_selector("button.btn").click()

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert.text
        finally: self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
