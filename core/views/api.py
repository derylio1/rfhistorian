from datetime import datetime
from core.models import Project, SingleExecution, SingleTestResult, SingleSuiteResult, Tag
from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid


class ProjectSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500)
    active = serializers.BooleanField()
    date_start = serializers.DateTimeField()

    def create(self,validated_data):
        return Project.objects.create(**validated_data)


class ProjectPostrSerializer(serializers.Serializer):
    uuid = serializers.HiddenField(default=uuid.uuid4())
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500)
    active = serializers.HiddenField(default=True)
    date_start = serializers.HiddenField(default=datetime.now())

    def create(self,validated_data):
        return Project.objects.create(**validated_data)

class SingleExecutionSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='uuid'
     )
    class Meta:
        model = SingleExecution
        fields = ['uuid', 'project', 'version', 'total_time', 'test_total', 'tests_passed', 'tests_failed', 'tests_skipped']

    def create(self,validated_data):
        return SingleExecution.objects.create(**validated_data)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']

class TestResultSerializer(serializers.ModelSerializer):
    suite_execution = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='uuid'
     )
    tag = TagSerializer(many=True, allow_null=True, required=False)
    error_message = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    class Meta:
        model = SingleTestResult
        fields = ['suite_execution', 'test_name', 'test_status', 'test_time', 'error_message', 'tag']

    def create(self,validated_data):
        
        if "tag" in validated_data.keys():
            tags_data = validated_data.pop('tag')
            test_result_object = SingleTestResult.objects.create(**validated_data)    
            for tag in tags_data:
                tag_object = self.add_tag_if_needed(tag["name"], self.context['project_uuid'], self.context['suite_execution'])
                test_result_object.tag.add(tag_object)
        else:
            test_result_object = SingleTestResult.objects.create(**validated_data)
        return test_result_object
    

    def add_tag_if_needed(self, tag_name, project_uuid, suite_execution):
        tags = Tag.objects.filter(name=tag_name, suite_execution__uuid=suite_execution, project__uuid=project_uuid)
        if tags:
            return tags.get()
        if not tags:
            suite_execution_object = SingleExecution.objects.filter(uuid=suite_execution).get()
            project_object = Project.objects.filter(uuid=project_uuid).get()
            created_tag = Tag.objects.create(name=tag_name, 
                                suite_execution=suite_execution_object, 
                                project=project_object)
            created_tag.save()
            return created_tag
        else:
            return tags

class SuiteResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleSuiteResult
        fields = ['name', 'test_status','total_time', 'test_total', 'tests_passed', 'tests_failed', 'tests_skipped']

    def create(self,validated_data):
        return SingleSuiteResult.objects.create(**validated_data)

class ProjectAPI(APIView):

    def get(self, request, format=None):
        snippets = Project.objects.all()
        serializer = ProjectSerializer(snippets, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = ProjectPostrSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SingleExecutionAPI(APIView):

    def get(self, request, project_uuid, format=None):        
        snippets = SingleExecution.objects.filter(project__uuid=project_uuid)
        serializer = SingleExecutionSerializer(snippets, many=True)        
        return Response(serializer.data)
    
    def post(self, request, project_uuid, format=None):
        serializer = SingleExecutionSerializer(data=request.data)
        if serializer.is_valid():
            project = Project.objects.filter(uuid=project_uuid).get()
            serializer.save(project=project)
            project.recent_execution_date = datetime.now()
            project.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TesteExecutionAPI(APIView):

    def get(self, request, project_uuid, suite_execution, format=None):
        snippets = SingleTestResult.objects.filter(suite_execution__uuid=suite_execution)
        serializer = TestResultSerializer(snippets, many=True)
        return Response(serializer.data)
    
    def post(self, request, project_uuid, suite_execution, format=None):
        serializer = TestResultSerializer(data=request.data, 
                                            context={'project_uuid': project_uuid,
                                                    'suite_execution': suite_execution})
        if serializer.is_valid():
            suite_execution = SingleExecution.objects.filter(uuid=suite_execution).get()
            serializer.save(suite_execution=suite_execution)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SuiteExecutionAPI(APIView):

    def get(self, request, project_uuid, suite_execution, format=None):
        snippets = SingleSuiteResult.objects.filter(suite_execution__uuid=suite_execution)
        serializer = SuiteResultSerializer(snippets, many=True)
        return Response(serializer.data)
    
    def post(self, request, project_uuid, suite_execution, format=None):
        serializer = SuiteResultSerializer(data=request.data)
        if serializer.is_valid():
            suite_execution = SingleExecution.objects.filter(uuid=suite_execution).get()
            serializer.save(suite_execution=suite_execution)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)