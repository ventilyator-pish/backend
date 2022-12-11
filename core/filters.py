from collections import defaultdict

import django_filters.rest_framework as filters
from django.db.models import Case, When

from core.models import StudentProfile
from core.utils.coverage import coverage
from core.utils.recomendations import collabarative_filtration


class StudentProfileFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='user.skills', method="filter_required_tags")

    def filter_required_tags(self, queryset, name, value) -> list[StudentProfile]:
        required_tags: list[int] = list(map(int, value.split(",")))

        students: list[int] = []
        student_tags = defaultdict(list)

        for student_id, tag_id in queryset.values_list("id", "user__skills__id"):
            student_tags[student_id].append(tag_id)
            students.append(student_id)

        filtration_coefficient = {s: 1 for s in students}

        if self.request.user:
            top_users = collabarative_filtration(self.request.user.company)

            for row in top_users:
                filtration_coefficient[row["student_id"]] = 1 + row["weight"]

        score = [coverage(student_tags[student], required_tags) * filtration_coefficient[student] for student in students]

        student_scores = sorted(zip(score, students), reverse=True)
        top_students_ids = [student for c, student in student_scores if c > 0]

        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(top_students_ids)])

        return queryset.filter(id__in=top_students_ids).order_by(preserved)

    class Meta:
        model = StudentProfile
        fields = ["id", "tags"]


class TagFilter(filters.FilterSet):
    keyword = filters.CharFilter(lookup_expr='icontains')


class ReviewFilter(filters.FilterSet):
    def filter_queryset(self, queryset):
        student_id = self.request.query_params.get("student", None)

        if not student_id:
            return queryset

        return queryset.filter(student__id=student_id)
