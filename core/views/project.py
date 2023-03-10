from django.http import HttpResponseRedirect
from django.views import generic
from core.models import Project, SingleExecution, Profile
from core.forms import ProjectForm
from django.utils.text import slugify


class ProjectList(generic.ListView):
    model =  Project
    extra_context = {'page_name': 'Project list', 
                    'project_page': 'active'}



    def get_queryset(self):
        if self.request.user.is_anonymous:
            return super().get_queryset().filter(project_access=0)

        if self.request.user.is_superuser:
            return super().get_queryset()
        
        if self.request.user.is_authenticated:
            user_access = Profile.objects.filter(user__id=self.request.user.id).get()
            return user_access.project_access.all().union(super().get_queryset().filter(project_access=0), all=True)

class ProjectDetail(generic.DetailView):
    model =  Project
    extra_context = {'page_name': 'Project details'}
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        suits = SingleExecution.objects.filter(project__uuid=self.object.uuid)
        versions = ', '.join(['"'+suite.version+'"'    for suite in suits])
        passed =  ', '.join([str(suite.tests_passed)   for suite in suits])
        failed =  ', '.join([str(suite.tests_failed)   for suite in suits])
        skipped =  ', '.join([str(suite.tests_skipped) for suite in suits])
        time =  ', '.join([str(suite.total_time)       for suite in suits])
        total = ', '.join([str(suite.test_total)       for suite in suits])
        print(versions)
        ctx['suites'] = suits
        ctx['version'] = versions
        ctx['passed'] = passed
        ctx['failed'] = failed
        ctx['skipped'] = skipped
        ctx['time'] = time
        ctx['test_total'] = total
        ctx['project_page'] = 'active'
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
