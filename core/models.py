import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import timedelta


# Create your models here.

def user_directory_path(instance, filename):
    return 'static/media/projects/{0}_{1}'.format(instance.uuid, filename)

class Project(models.Model):
    PROJECT_ACCESS = (
        ('PUBLIC', "Public"),
        ('PRIVATE', "Private"),
    )
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=100, blank=False)
    access = models.CharField(max_length=7, choices=PROJECT_ACCESS, name='project_access', default=0)
    name = models.CharField(max_length=200, unique=True, name='name')
    description = models.TextField(max_length=500, unique=True, name='description')
    date_start = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    recent_execution_date = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('projects:list')
    
    def get_project_detail_url(self):
        return reverse('projects:detail', kwargs={'slug':self.slug})
    
    def get_success_url(self):
        return reverse('projects:detail', kwargs={'slug':self.slug})

    def __str__(self) -> str:
        return self.name

class SingleExecution(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, verbose_name='prject', on_delete=models.CASCADE)
    version =  models.CharField(max_length=200, unique=False, verbose_name='software version')
    total_time = models.FloatField(verbose_name='time total')
    test_total = models.IntegerField(verbose_name='tests total')
    tests_passed = models.IntegerField(verbose_name='tests passed')
    tests_failed = models.IntegerField(verbose_name='tests failed')
    tests_skipped = models.IntegerField(verbose_name='tests skipped')
    date_executed = models.DateTimeField(auto_now=True)
    date_uploaded = models.DateTimeField(auto_now=True)

    def get_perc_passed(self):
        return int( (int(self.tests_passed)/int(self.test_total)) *100 )
    
    def get_perc_passed_width(self):
        return (int( (int(self.tests_passed)/int(self.test_total)) *100 )//10)*10
    
    def get_perc_failed(self):
        return int( (int(self.tests_failed)/int(self.test_total)) *100 )

    def get_perc_failed_width(self):
        return (int( (int(self.tests_failed)/int(self.test_total)) *100 )//10)*10
    
    def get_perc_skipped(self):
        return int( (int(self.tests_skipped)/int(self.test_total)) *100 )
    
    def get_perc_skipped_width(self):
        return (int( (int(self.tests_skipped)/int(self.test_total)) *100 )//10)*10

    def __str__(self) -> str:
        return self.project.name+"_"+str(self.uuid)+"_"+str(self.date_uploaded)
    
    def get_execution_list_url(self):
        return reverse('projects:executions:list', kwargs={'slug': self.project.slug})
    
    def get_execution_details_url(self):
        return reverse('projects:executions:details', kwargs={'slug': self.project.slug,
                                                        'execution_uuid':self.uuid})
    def get_execution_seconds(self):
        return timedelta(seconds=self.test_total)

class Tag(models.Model):
    suite_execution = models.ForeignKey(SingleExecution, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class TestCaseObject(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024, verbose_name='test case name')

class SingleTestResult(models.Model):
    RESULT_STATUS = (
        ('PASS', "PASS"),
        ('FAIL', "FAIL"),
        ('SKIP', "SKIP"),
    )
    #Test_Id, Execution_Id, Test_Name, Test_Status, Test_Time, Test_Error, Test_Tag
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suite_execution = models.ForeignKey(SingleExecution, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, name='test_name')
    status = models.CharField(max_length=4, choices=RESULT_STATUS, name='test_status')
    test_time = models.FloatField(verbose_name="execution time")
    error_message = models.CharField(max_length=1024, name='error_message', blank=True, null=True)
    tag = models.ManyToManyField(Tag, blank=True,null=True, default=None)

    def get_comments(self):
        return Comment.objects.filter(test=self)
    
    def get_comments_count(self):
        return len(Comment.objects.filter(test=self))
    
    def get_add_comment_url(self):
        return reverse('projects:executions:comments:create', kwargs={'slug': self.suite_execution.project.slug,
                                                        'execution_uuid':self.uuid,
                                                        'test_uuid':self.uuid})
    def __str__(self):
        return self.test_name + " " + str(self.suite_execution.date_executed)
    
    def get_tag_count(self):
        return self.tag.count()
    
    def get_tag_data(self):
        return self.tag.all()

class SingleSuiteResult(models.Model):
    RESULT_STATUS = (
        ('PASS', "PASS"),
        ('FAIL', "FAIL"),
        ('SKIP', "SKIP"),
    )
    #Test_Id, Execution_Id, Test_Name, Test_Status, Test_Time, Test_Error, Test_Tag
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suite_execution = models.ForeignKey(SingleExecution, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=4, choices=RESULT_STATUS, name='test_status')
    total_time = models.FloatField()
    test_total = models.IntegerField()
    tests_passed = models.IntegerField()
    tests_failed = models.IntegerField()
    tests_skipped = models.IntegerField()
    


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    project_access = models.ManyToManyField(Project)

    def get_project_count(self):
        return len(self.project_access)
    
    def get_update_url(self):
        return reverse('profiles:update', kwargs={'user_id': self.user.id})

class Comment(models.Model):
    test = models.ForeignKey(SingleTestResult, on_delete=models.CASCADE)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self' , null=True , blank=True , on_delete=models.CASCADE , related_name='replies')

    class Meta:
        ordering=['-date_posted']

    def __str__(self):
        return str(self.author) + ' comment ' + str(self.content)

    @property
    def children(self):
        return Comment.objects.filter(parent=self).reverse()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False
