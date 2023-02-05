"""rfhistorian URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from core.views.project import ProjectList, ProjectCreate, ProjectDetail
from core.views.suites import SuitesExecutionList, SuiteExecutionDetails
from core.views.profile import ProfileList, ProfiletDetail, ProfileUpdate
from core.views.test_statistic import TestStatisticDetails
from core.views.register import RegisterUser
from core.views.comment import CommentCreate
from core.views.dashboard import Dashboard
from core.views.api import ProjectAPI, SingleExecutionAPI, TesteExecutionAPI, SuiteExecutionAPI



result_api = [#SuiteExecutionAPI
    path('<uuid:suite_execution>/tests', TesteExecutionAPI.as_view(), name='tests'),
    path('<uuid:suite_execution>/suites', SuiteExecutionAPI.as_view(), name='suites'),
]



suite_execution_api_urls = [
    path('<uuid:project_uuid>/execution', SingleExecutionAPI.as_view(), name='list'),
    path('<uuid:project_uuid>/execution/', include((result_api, 'results'))),
]

api_urls = [
    path('projects/', ProjectAPI.as_view(), name="project"),
    path('projects/', include((suite_execution_api_urls, 'execution'))),
]

test_comments_urls = [
    path('add-comment', CommentCreate.as_view(), name="create")
]

execution_urls = [
    path('suites', SuitesExecutionList.as_view(), name='list'),
    path('<uuid:execution_uuid>/details', SuiteExecutionDetails.as_view(), name='details'),
    path('<uuid:execution_uuid>/test/<uuid:test_uuid>/', include((test_comments_urls, 'comments'))),
]
test_statistics = [
    path('<uuid:test_uuid>', TestStatisticDetails.as_view(), name='details'),
]

project_urls = [
    path('', ProjectList.as_view(), name='list'),
    path('create', ProjectCreate.as_view(), name='create'),
    path('<slug:slug>', ProjectDetail.as_view(), name='detail'),
    path('<slug:slug>/executions/', include((execution_urls, 'executions'))),
    path('<slug:slug>/statistics/', include((test_statistics, 'statistics'))),
]

profile_urls = [
    path('', ProfileList.as_view(), name='list'),
    path('<int:user_id>/details', ProfiletDetail.as_view(), name='details'),
    path('<int:user_id>/update', ProfileUpdate.as_view(), name='update'),
]

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('projects/', include((project_urls,'projects'))),
    path('login/',views.LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/',views.LogoutView.as_view(), name='logout'),
    path('register/',RegisterUser.as_view(template_name="signup.html"), name='signup'),
    path('profiles/', include((profile_urls,'profiles'))),
    path('admin/', admin.site.urls),
    path('api/', include((api_urls, 'api'))),
    path('api-auth/', include('rest_framework.urls'))
]
