from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from core.models import Profile
from core.forms import RegisterForm
from django.utils.text import slugify
from django.contrib.auth.models import User

# Create your views here.


class RegisterUser(generic.CreateView):
    model = User
    form_class = RegisterForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        Profile.objects.create(user=self.object).save()
        return redirect("/")