from unittest import skip

from django.contrib.auth.models import User, Group
from django.test import TestCase
from core.models import Profile, Project
from django.urls import reverse
import logging
from core.tests.data_init import TestDataInit
import time

class TestProject(TestDataInit, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.power_user = cls.make_superuser()
        cls.simple_user = cls.make_user_with_profile()
        cls.example_project = cls.make_project(cls.power_user)
        cls.post_data = {
            'name': 'Example Project 2',
            'description': 'Description Foo Bar',
        }

    def test_project_list_as_annonymous(self):
        get_resp = self.client.get(reverse('projects:list'))
        self.assertEqual(200, get_resp.status_code)
    
    def test_project_list_as_superuser(self):
        self.client.login(username='admintest', password='qweasd')
        get_resp = self.client.get(reverse('projects:list'))
        self.assertEqual(200, get_resp.status_code)

    def test_project_list_as_simple_user(self):
        self.client.login(username='user', password='qweasd')
        get_resp = self.client.get(reverse('projects:list'))
        self.assertEqual(200, get_resp.status_code)
    
    def test_project_details(self):
        self.client.login(username='admintest', password='qweasd')
        get_resp = self.client.get(self.example_project.get_project_detail_url())
        self.assertEqual(200, get_resp.status_code)
        self.assertContains(get_resp, self.example_project.name)
        #self.assertContains(get_resp, self.example_project.description)
        #self.assertContains(get_resp, self.example_project.date_start)
    
    def test_project_create(self):
        self.client.login(username='admintest', password='qweasd')
        get_resp = self.client.get(reverse('projects:create'))
        self.assertEqual(200, get_resp.status_code)
        post_resp = self.client.post(reverse('projects:create'), data=self.post_data)
        self.assertEqual(302, post_resp.status_code)
        last_project = Project.objects.first()
        print("Last project", last_project)
        self.assertEqual(self.post_data['name'], last_project.name)
        self.assertEqual(self.post_data['description'], last_project.description)