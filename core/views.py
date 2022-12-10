import django_filters.rest_framework as filters
from rest_framework.viewsets import ModelViewSet

from core.filters import StudentProfileFilter
from core.models import Project, StudentProfile
from core.serializers import ProjectSerializer, StudentProfileSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class StudentProfileViewSet(ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer

    filterset_class = StudentProfileFilter
