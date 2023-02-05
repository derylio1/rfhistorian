from django.http import HttpResponseRedirect
from django.views import generic
from core.models import TestCaseObject, SingleTestResult


class TestStatisticDetails(generic.DetailView):
    model = TestCaseObject
    extra_context = {'page_name': 'Test statistic details'}
    slug_field = 'uuid'
    slug_url_kwarg = 'test_uuid'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        test_execution_list = SingleTestResult.objects.filter(test__uuid=self.object.uuid)
        version_list = ', '.join(['"'+ suite.suite_execution.version +'"'    for suite in test_execution_list])
        execution_time_list = ', '.join(['"'+ str(suite.execution_time) +'"'    for suite in test_execution_list])
        breadcrumbs = [{
                        'name': self.object.project.name,
                        'url':  self.object.project.get_project_detail_url()}
                    ]
        ctx['breadcrumbs'] = breadcrumbs
        ctx['version'] = version_list
        ctx['execution_time'] = execution_time_list
        ctx['test_execution'] = test_execution_list
        
        return ctx