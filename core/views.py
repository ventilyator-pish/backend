from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.decorators import action
from rest_framework.validators import ValidationError
from rest_framework.response import Response

from core.filters import StudentProfileFilter, TagFilter
from core.models import Company, Tag, Project, StudentProfile, StudentRequest, Review, User
from core.serializers import (
    CompanySerializer,
    ReviewSerializer,
    TagSerializer,
    ProjectSerializer,
    StudentProfileSerializer,
    StudentRequestSerializer,
)
from core.utils.parse_tags import parse_url_tags


class TagViewSet(GenericViewSet, ListModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    filterset_class = TagFilter


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @action(methods=["POST"], detail=True, url_path="request")
    def make_request(self, request, *args, **kwargs):
        if not request.user or not request.user.studentprofile:
            raise ValidationError("Should be a student")

        student_profile = request.user.studentprofile
        project: Project = self.get_object()

        StudentRequest.objects.get_or_create(
            student_profile=student_profile,
            project=project,
            initiator=User.UserType.STUDENT
        )

        return Response({"status": "ok!"})


class StudentProfileViewSet(ModelViewSet):
    queryset = StudentProfile.objects.all().prefetch_related(
        "user__skills",
        "user__interest_tags"
    ).select_related("user")

    serializer_class = StudentProfileSerializer

    filterset_class = StudentProfileFilter

    @action(methods=["POST"], detail=True, url_path="make_response")
    def make_response(self, request, *args, **kwargs):
        if not request.user or not request.user.company:
            raise ValidationError("You should has company")

        if "project_id" not in request.data:
            raise ValidationError("You should specify project_id")

        if "decision" not in request.data or request["decision"] not in StudentRequest.StudentRequestState.choices:
            raise ValidationError(f"Decision key should be in {StudentRequest.StudentRequestState.choices}")

        project = Project.objects.get()
        company = request.user.company

        if project.company != company:
            raise ValidationError("You should by an owner of a project")

        student_profile = self.get_object()

        student_request = StudentRequest.objects.filter(
            student_profile=student_profile,
            project=project,
        ).first()

        if not student_request:
            raise ValidationError("There is no request from student")

        state = request.data["decision"]
        project.team.add(student_profile)
        student_request.state = state
        student_request.save()

        return Response({"status": "ok"})


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


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class StudentRequestViewSet(ModelViewSet):
    queryset = StudentRequest.objects.all()
    serializer_class = StudentRequestSerializer