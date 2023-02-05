from django.http import HttpResponseRedirect
from django.views import generic
from core.models import Project, Profile
from core.forms import ProfileForm
from django.utils.text import slugify


class ProfileList(generic.ListView):
    model =  Profile
    extra_context = {'page_name': 'Profiles list', 
                    'profile_page': 'active'}


class ProfiletDetail(generic.DetailView):
    model =  Profile
    extra_context = {'page_name': 'Profile details'}
    slug_field = 'id'
    slug_url_kwarg = 'user_id'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

class ProfileUpdate(generic.CreateView):
    model = Profile
    form_class = ProfileForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        return HttpResponseRedirect('/')
