from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin

from core.filters import StudentProfileFilter
from core.models import Tag, Project, StudentProfile
from core.serializers import TagSerializer, ProjectSerializer, StudentProfileSerializer


class TagViewSet(GenericViewSet, ListModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class StudentProfileViewSet(ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer

    filterset_class = StudentProfileFilter
