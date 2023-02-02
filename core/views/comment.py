from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from core.models import SingleTestResult, Comment
from core.forms import CommentForm
from django.utils.text import slugify


class CommentCreate(generic.CreateView):
    model = Comment
    form_class = CommentForm
    test = None

    def dispatch(self, request, *args, **kwargs):
        self.test = get_object_or_404(SingleTestResult.objects.filter(uuid=kwargs['test_uuid']))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.test = self.test
        self.object.save()
        return HttpResponseRedirect(reverse('projects:executions:details', kwargs={'slug': self.object.test.suite_execution.project.slug,
                                                        'execution_uuid':self.object.test.suite_execution.uuid}))
