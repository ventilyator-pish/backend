from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.decorators import action
from rest_framework.validators import ValidationError
from rest_framework.response import Response

from core.filters import StudentProfileFilter, TagFilter
from core.models import Company, Tag, Project, StudentProfile, StudentRequest, Review, User, CrowdFundingDonation, CrowdFunding
from core.serializers import (
    CompanySerializer,
    ReviewSerializer,
    TagSerializer,
    ProjectSerializer,
    StudentProfileSerializer,
    StudentRequestSerializer,
    CrowdFundingSerializer,
)
from core.utils.parse_tags import parse_url_tags


class TagViewSet(GenericViewSet, ListModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    filterset_class = TagFilter


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all().select_related("crowdfunding")
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

    @action(methods=["POST"], detail=True, url_path="donate")
    def donate(self, request, *args, **kwargs):
        project = self.get_object()
        if not project.crowdfunding:
            raise ValidationError("There is no crowdfunding")

        if "amount" not in request.data:
            raise ValidationError("There is no amount")

        crowdfunding = project.crowdfunding
        CrowdFundingDonation.objects.create(
            crowdfunding=crowdfunding,
            amount=request.data["amount"],
            author=self.request.user
        )


class StudentProfileViewSet(ModelViewSet):
    queryset = StudentProfile.objects.all().prefetch_related(
        "user__skills",
        "user__interest_tags"
    ).select_related("user")

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


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class StudentRequestViewSet(ModelViewSet):
    queryset = StudentRequest.objects.all()
    serializer_class = StudentRequestSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.exclude(state=StudentRequest.StudentRequestState.OPEN)
        return queryset

    @action(methods=["POST"], detail=True, url_path="make_response")
    def make_response(self, request, *args, **kwargs):
        if not request.user or not request.user.company:
            raise ValidationError("You should has company")

        if "decision" not in request.data or request.data["decision"] not in [
            StudentRequest.StudentRequestState.ACCEPTED,
            StudentRequest.StudentRequestState.REJECTED,
        ]:
            raise ValidationError(f"Decision key should be in {StudentRequest.StudentRequestState.choices}")

        student_request = self.get_object()
        project = student_request.project
        company = request.user.company

        if project.company != company:
            raise ValidationError("You should by an owner of a project")

        student_profile = student_request.student

        student_request = StudentRequest.objects.filter(
            student=student_profile,
            project=project,
        ).first()

        if not student_request:
            raise ValidationError("There is no request from student")

        state = request.data["decision"]
        project.team.add(student_profile)
        student_request.state = state
        student_request.save()

        return Response({"status": "ok"})


class CrowdFoundingViewSet(ModelViewSet):
    queryset = CrowdFunding.objects.all()
    serializer_class = CrowdFundingSerializer

    class Meta:
        model = CrowdFunding
        fields = "__all__"
