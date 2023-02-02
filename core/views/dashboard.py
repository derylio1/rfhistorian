from django.shortcuts import render
from django.views import generic
from core.models import Project, SingleExecution, Profile
# Create your views here.

class Dashboard(generic.TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        projects = None
        if self.request.user.is_anonymous:
            projects = Project.objects.filter(project_access=0)

        elif self.request.user.is_superuser:
            projects = Project.objects.get_queryset()
        
        elif self.request.user.is_authenticated:
            user_access = Profile.objects.filter(user__id=self.request.user.id).get()
            projects = user_access.project_access.all().union(Project.objects.filter(project_access=0), all=True)

        project_list = projects[:4]
        ctx['project_list'] = project_list
        ctx['dashboard_page'] = 'active'
        ctx['test_execution_list'] = SingleExecution.objects.all()[:10:-1]
        ctx['page_name'] = "Dashboard"
        return ctx
    

