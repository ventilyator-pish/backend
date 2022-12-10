from rest_framework.serializers import ModelSerializer

from core.models import StudentProfile, Project


class StudentProfileSerializer(ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = "__all__"


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
