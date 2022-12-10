from rest_framework import serializers

from core.models import Company, User, Tag, StudentProfile, Project
from core.utils.coverage import coverage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


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
