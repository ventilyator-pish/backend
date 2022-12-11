import random

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.decorators import action
from rest_framework.validators import ValidationError
from rest_framework.response import Response

from core.exceptions import NotEnoughStudents
from core.filters import StudentProfileFilter, TagFilter, ReviewFilter
from core.models import Company, Tag, Project, StudentProfile, StudentRequest, Review, User, CrowdFundingDonation, \
    CrowdFunding, CompanyStudentEmotion
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

    filterset_fields = ["company_id"]

    def create(self, request, *args, **kwargs):
        image = request.data.get("image", b"")
        self.request.image = image
        return super().create(request, *args, **kwargs)

    @action(methods=["POST"], detail=True, url_path="request")
    def make_request(self, request, *args, **kwargs):
        if not request.user or not request.user.studentprofile:
            raise ValidationError("Should be a student")

        student_profile = request.user.studentprofile
        project: Project = self.get_object()

        StudentRequest.objects.get_or_create(
            student=student_profile,
            company=project.company,
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

        return Response({"status": "ok"})


class StudentProfileViewSet(ModelViewSet):
    queryset = StudentProfile.objects.all().prefetch_related(
        "user__skills",
        "user__interest_tags"
    ).select_related("user")

    serializer_class = StudentProfileSerializer

    filterset_class = StudentProfileFilter

    @action(methods=["POST"], detail=True, url_path="invite")
    def invite(self, request, *args, **kwargs):
        if not request.user or not request.user.company:
            raise ValidationError("Should be a company")

        if "project_id" not in self.request.data:
            raise ValidationError("You should specify project_id")

        student_profile = self.get_object()
        project = Project.objects.get(id=self.request.data["project_id"])

        StudentRequest.objects.get_or_create(
            student=student_profile,
            company=request.user.company,
            project=project,
            initiator=User.UserType.COMPANY
        )

        return Response({"status": "ok!"})


class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @action(methods=["POST"], detail=True, url_path="update_tags")
    def update_tags(self, request, *args, **kwargs):
        company: Company = self.get_object()

        if "url" not in request.data:
            raise ValidationError("You should specify url")

        url = request.data["url"]

        start_tag_count = company.interest_tags.count()

        new_tags = parse_url_tags(url, Tag.objects.all())
        company.interest_tags.add(*new_tags)
        company.save()

        end_tag_count = company.interest_tags.count()

        return Response({"status": "ok", "delta": end_tag_count - start_tag_count})


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    filterset_class = ReviewFilter


class StudentRequestViewSet(ModelViewSet):
    queryset = StudentRequest.objects.all()
    serializer_class = StudentRequestSerializer

    def get_queryset(self):
        queryset = self.queryset.exclude(state=StudentRequest.StudentRequestState.OPEN)

        initiator = self.request.query_params.get("initiator", None)
        obj_id = int(self.request.query_params.get("id", 0))

        if not initiator:
            return queryset

        if initiator == User.UserType.STUDENT:
            return queryset.filter(project_id=obj_id)

        return queryset.filter(student_id=obj_id)

    @action(methods=["POST"], detail=True, url_path="update_tags")
    def update_tags(self, request, *args, **kwargs):
        user = self.request.user

        if "url" not in request.data:
            raise ValidationError("You should specify url")

        url = request.data["url"]

        start_tag_count = user.interest_tags.count()

        new_tags = parse_url_tags(url, Tag.objects.all())
        user.interest_tags.add(*new_tags)
        user.save()

        end_tag_count = user.interest_tags.count()

        return Response({"status": "ok", "delta": end_tag_count - start_tag_count})

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


class TinderViewSet(GenericViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer

    @action(methods=["GET"], detail=False, url_path="random_pick")
    def get_random(self):
        already_picked_ids = CompanyStudentEmotion.objects.values_list("student__id", flat=True)
        students = StudentProfile.objects.exclude(id__in=already_picked_ids).values_list("id", flat=True)

        if not students:
            raise NotEnoughStudents()

        student_id = random.choice(students)

        return StudentProfile.objects.get(id=student_id)

    def _set_emotion(self, emotion: str) -> None:
        student = self.get_object()

        CompanyStudentEmotion.objects.create(
            student=student,
            company=self.request.user.company,
            emotion=emotion,
        )

    @action(methods=["GET"], detail=True, url_path="like")
    def like(self):
        self._set_emotion(CompanyStudentEmotion.CompanyEmotion.LIKE)
        return Response({"status": "ok"})

    @action(methods=["GET"], detail=True, url_path="dislike")
    def dislike(self):
        self._set_emotion(CompanyStudentEmotion.CompanyEmotion.DISLIKE)
        return Response({"status": "ok"})
