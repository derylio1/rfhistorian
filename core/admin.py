from django.contrib import admin
from core.models import Project, SingleExecution, SingleTestResult, Profile, TestCaseObject, Comment, Tag
# Register your models here.

admin.site.register(Project)
admin.site.register(SingleExecution)
admin.site.register(SingleTestResult)
admin.site.register(Profile)
admin.site.register(TestCaseObject)
admin.site.register(Comment)
admin.site.register(Tag)