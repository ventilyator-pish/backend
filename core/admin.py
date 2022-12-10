from django.contrib import admin

from core.models import StudentProfile, User, Company, Tag


admin.site.register(StudentProfile)
admin.site.register(User)
admin.site.register(Company)
admin.site.register(Tag)
