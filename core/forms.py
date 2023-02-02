from django import forms
from core.models import Project, Comment, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CoreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            css_class = field.widget.attrs.get('class', '')
            css_class += ' form-control'
            field.widget.attrs['class'] = css_class

    def as_core(self):
        "Return this form rendered as DIVs"
        return self._html_output(
            normal_row='<div class="form-group row" %(html_class_attr)s>'
                            '<label class="col-sm-4 col-form-label">%(label)s</label>'
                            '<div class="col-lx-8">%(help_text)s%(errors)s%(field)s</div>'
                       '</div>',
            error_row='<span class="error">%s</span>',
            row_ender='',
            help_text_html='<br><span class="helptext">%s</span>',
            errors_on_separate_row=False,
        )

class SimpleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            css_class = field.widget.attrs.get('class', '')
            css_class += ' form-control'
            field.widget.attrs['class'] = css_class

    def as_core(self):
        "Return this form rendered as DIVs"
        return self._html_output(
            normal_row='<div class="form-group row" %(html_class_attr)s>'
                            '<label class="col-sm-4 col-form-label">%(label)s</label>'
                            '<div class="col-lx-8">%(help_text)s%(errors)s%(field)s</div>'
                       '</div>',
            error_row='<span class="error">%s</span>',
            row_ender='',
            help_text_html='<br><span class="helptext">%s</span>',
            errors_on_separate_row=False,
        )

class ProjectForm(CoreForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
    

class CommentForm(CoreForm):
    class Meta:
        model = Comment
        fields = ['content']

class RegisterForm(UserCreationForm, SimpleForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class ProfileForm(CoreForm):
    class Meta:
        model = Profile
        fields = ['project_access']