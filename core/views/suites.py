from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic
from core.models import Project, SingleExecution, SingleTestResult, SingleSuiteResult
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from core.forms import ProjectForm


class SuitesExecutionList(generic.ListView):
    model =  SingleExecution
    extra_context = {'page_name': 'Execution list'}
    project = None

    def dispatch(self, request, *args, **kwargs):
        self.project = Project.objects.filter(slug=kwargs['slug']).get()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset().filter(project=self.project)
        print(qs)
        return qs

class SuiteExecutionDetails(generic.DetailView):
    model = SingleExecution
    slug_field = 'uuid'
    slug_url_kwarg = 'execution_uuid'
    extra_context = {'page_name': 'Execution details'}
    project = None

    def get_queryset(self):
        return super().get_queryset().filter(project=self.project)
        
    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project.objects.filter(slug=kwargs['slug']))
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        test_list = SingleTestResult.objects.filter(suite_execution__uuid=self.object.uuid)
        suites = SingleSuiteResult.objects.filter(suite_execution__uuid=self.object.uuid)
        ctx['test_list'] = test_list
        ctx['suites'] = suites
        breadcrumbs = [{
                        'name': self.object.project.name,
                        'url':  self.object.project.get_project_detail_url()}
                    ]
        ctx['breadcrumbs'] = breadcrumbs
        return ctx
    