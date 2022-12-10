from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.decorators import action
from rest_framework.validators import ValidationError
from rest_framework.response import Response

from core.filters import StudentProfileFilter, TagFilter
from core.models import Company, Tag, Project, StudentProfile
from core.serializers import CompanySerializer, TagSerializer, ProjectSerializer, StudentProfileSerializer
from core.utils.parse_tags import parse_url_tags


class TagViewSet(GenericViewSet, ListModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    filterset_class = TagFilter


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class StudentProfileViewSet(ModelViewSet):
    queryset = StudentProfile.objects.all().prefetch_related("user__skills").select_related("user")
    serializer_class = StudentProfileSerializer

    filterset_class = StudentProfileFilter


class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @action(methods=["POST"], detail=True, url_path="update_tags")
    def update_tags(self, request, *args, **kwargs):
        company: Company = self.get_object()

        if "url" not in request.data:
            raise ValidationError("You should specify url")

        url = request.data["url"]

        new_tags = parse_url_tags(url, Tag.objects.all())
        company.interest_tags.add(*new_tags)
        company.save()

        return Response({"status": "ok"})