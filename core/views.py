from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins

from core.models import Project, StudentProfile
from core.serializers import ProjectSerializer, StudentProfileSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class StudentProfileViewSet(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
