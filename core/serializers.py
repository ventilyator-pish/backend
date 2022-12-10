from rest_framework import serializers

from core.exceptions import IsNotCompanyException
from core.models import Company, User, Tag, StudentProfile, Project, Review
from core.utils.coverage import coverage


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class StudentProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    coverage = serializers.SerializerMethodField()

    interest_tags = TagSerializer(source="user.interest_tags", many=True, read_only=True)
    skills = TagSerializer(source="user.interest_tags", many=True, read_only=True)

    def get_coverage(self, obj: StudentProfile):
        tags = self.context["request"].query_params.get("tags", "").split(",")
        tags = list(map(int, tags)) if tags[0] else []

        return coverage(obj.user.skills.values_list("id", flat=True), tags)

    class Meta:
        model = StudentProfile
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    company = serializers.ReadOnlyField()
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())

    def validate(self, attrs):
        request = self.context["request"]

        if not request.user or not request.user.company:
            raise IsNotCompanyException()

        return attrs

    def create(self, validated_data: dict) -> Review:
        request = self.context["request"]

        validated_data["company"] = request.user.company
        instance = super().create(validated_data)

        return instance

    class Meta:
        model = Review
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    studentprofile = StudentProfileSerializer()
    company = CompanySerializer()

    interest_tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), write_only=True)
    skills_tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), write_only=True)

    class Meta:
        model = User
        fields = "__all__"
        ref_name = "custom_user_serializer"
