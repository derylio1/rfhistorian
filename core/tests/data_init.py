#import boto3
#import moto
from django.contrib.auth.models import User, Group
#from core.business_logic.group_manager import GroupManager
from core.models import Project, Profile, SingleExecution, SingleSuiteResult, SingleTestResult
from datetime import date, datetime
from django.utils.text import slugify

from rfhistorian import settings


class TestDataInit:

    @classmethod
    def make_superuser(cls) -> User:
        user = User.objects.create_superuser('admintest', password='qweasd')
        return user
    
    @classmethod
    def make_user_with_profile(cls) -> User:
        user = User.objects.create_user('user', password='qweasd')
        profile = Profile.objects.create(user=user)
        return user
    
    @classmethod
    def make_project(cls, user) -> User:
        defaults = dict(
            name="Example project",
            slug=slugify("Example project"),
            project_access="Public",
            description="Example description",
            created_by=user
        )
        return Project.objects.create(**defaults)
