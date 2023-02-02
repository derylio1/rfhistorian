from unittest import skip

from django.contrib.auth.models import User, Group
from django.test import TestCase
from core.models import Profile, Profile
import logging
#from polls.tests.data_init import TestDataInit

class TestSignup(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_signup(self):
        get_resp = self.client.get('/register/')
        self.assertEqual(200, get_resp.status_code)
        register_data = {
            'username' : 'januszex',
            'email':     'foo@bar.com',
            'password1' :'password1@@',
            'password2' :'password1@@',
        }
        post_resp = self.client.post('/register/', data=register_data)
        self.assertEqual(302, post_resp.status_code)
        last_profile = Profile.objects.last()

        self.assertEqual(register_data['username'],    last_profile.user.username)
    

    def test_signup_invalid_data(self):
        get_resp = self.client.get('/register/')
        self.assertEqual(200, get_resp.status_code)
        update_data = {
            'username' : '12',
            'password1' :'',
            'password2' :'password1@@',
        }
        post_resp = self.client.post('/register/', data=update_data)
        self.assertEqual(200, post_resp.status_code)