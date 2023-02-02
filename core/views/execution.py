from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic
from core.models import Project, SingleExecution, SingleTestResult
from core.forms import ProjectForm
from django.utils.text import slugify


class ExecutionList(generic.ListView):
    model =  SingleExecution
    extra_context = {'page_name': 'Execution list', 
                    'project_page': 'active'}


class ExecutionDetail(generic.DetailView):
    model =  SingleExecution
    extra_context = {'page_name': 'Execution details'}
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        test_results = SingleTestResult.objects.filter(suite_execution__uuid=self.object.uuid)
        return ctx

class ProjectCreate(generic.CreateView):
    model = Project
    form_class = ProjectForm
    

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.slug = slugify(self.object.name)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
