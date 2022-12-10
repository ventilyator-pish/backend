from rest_framework import serializers

from core.models import StudentProfile, Project
from core.utils.coverage import coverage


class StudentProfileSerializer(serializers.ModelSerializer):
    coverage = serializers.SerializerMethodField()

    def get_coverage(self, obj: StudentProfile):
        tags = self.context["request"].query_params.get("tags", "").split(",")
        tags = list(map(int, tags))

        return coverage(obj.user.skills.values_list("id", flat=True), tags)

    class Meta:
        model = StudentProfile
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
