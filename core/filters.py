from collections import defaultdict

import django_filters.rest_framework as filters
from django.db.models import Case, When

from core.models import StudentProfile
from core.utils.coverage import coverage


class StudentProfileFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='user.skills', method="filter_required_tags")

    def filter_required_tags(self, queryset, name, value) -> list[StudentProfile]:
        required_tags: list[int] = list(map(int, value.split(",")))

        students: list[int] = []
        student_tags = defaultdict(list)

        for student_id, tag_id in queryset.values_list("id", "user__skills__id"):
            student_tags[student_id].append(tag_id)
            students.append(student_id)

        coverages = [coverage(student_tags[student], required_tags) for student in students]
        student_coverages = sorted(zip(coverages, students), reverse=True)
        top_students_ids = [student for c, student in student_coverages if c > 0]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(top_students_ids)])

        return queryset.filter(id__in=top_students_ids).order_by(preserved)

    class Meta:
        model = StudentProfile
        fields = ["id", "tags"]
