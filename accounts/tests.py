from django.test import TestCase
from django.contrib.auth.models import User
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
