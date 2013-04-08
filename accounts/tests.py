from django.test import TestCase, LiveServerTestCase
from django.contrib.auth.models import User
from guardian.shortcuts import assign
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from socialregistration.contrib.github.models import GithubProfile
from accounts.models import Profile


class ModelCase(TestCase):
    """Test model"""

    def setUp(self):
        """Create initial"""
        self.user = User.objects.create(username='test')
        Profile.objects.create(user=self.user)

    def test_no_social(self):
        """Test no social"""
        self.assertFalse(self.user.profile.is_social())

    def test_has_social(self):
        """Test has social"""
        GithubProfile.objects.create(
            user=self.user,
            github='github',
        )
        self.assertTrue(self.user.profile.is_social())


class ClientSideCase(LiveServerTestCase):
    """Test client site part of accounts"""

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
        Profile.objects.create(user=self.user)
        assign('change_profile', self.user, self.user.get_profile())
        assign('change_user', self.user, self.user)

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

    def test_registration(self):
        """Test registration"""
        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_link_text("sign up").click()
        driver.find_element_by_id("id_username").clear()
        driver.find_element_by_id("id_username").send_keys("test")
        driver.find_element_by_id("id_email").clear()
        driver.find_element_by_id("id_email").send_keys("test@test.test")
        driver.find_element_by_id("id_password1").clear()
        driver.find_element_by_id("id_password1").send_keys("test")
        driver.find_element_by_id("id_password2").clear()
        driver.find_element_by_id("id_password2").send_keys("test")
        driver.find_element_by_css_selector("button.btn").click()
        self.assertEqual(
            User.objects.filter(username='test').count(), 1,
        )

    def test_username_authentication(self):
        """Test auth by username"""
        driver = self.driver
        self._login()
        driver.get(self.base_url + "/")
        driver.find_element_by_link_text("sign out").click()

    def test_email_authentication(self):
        """Test email authentication"""
        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_link_text("sign in").click()
        driver.find_element_by_id("id_identification").clear()
        driver.find_element_by_id("id_identification").send_keys("test_user@test.test")
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys("test")
        driver.find_element_by_css_selector("button.btn").click()
        driver.find_element_by_link_text("sign out").click()

    def test_edit_profile(self):
        """Test edit profile"""
        self._login()
        name = "test name"
        last_name = "test last"
        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_link_text("test_user").click()
        driver.find_element_by_link_text("Edit details").click()
        driver.find_element_by_id("id_first_name").clear()
        driver.find_element_by_id("id_first_name").send_keys(name)
        driver.find_element_by_id("id_last_name").clear()
        driver.find_element_by_id("id_last_name").send_keys(last_name)
        driver.find_element_by_css_selector("button.btn").click()

        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.first_name, name)
        self.assertEqual(user.last_name, last_name)

    def test_change_password(self):
        """Test change password"""
        self._login()
        password = "test1"
        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_link_text("test_user").click()
        driver.find_element_by_link_text("Change password").click()
        driver.find_element_by_id("id_old_password").clear()
        driver.find_element_by_id("id_old_password").send_keys("test")
        driver.find_element_by_id("id_new_password1").clear()
        driver.find_element_by_id("id_new_password1").send_keys(password)
        driver.find_element_by_id("id_new_password2").clear()
        driver.find_element_by_id("id_new_password2").send_keys(password)
        driver.find_element_by_css_selector("button.btn").click()

        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password(password))

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
