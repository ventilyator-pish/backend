from django.db import models
from django.contrib.auth.models import AbstractUser


class Tag(models.Model):
    """ Skills or Professions """
    keyword = models.CharField(max_length=127)
    color = models.CharField(max_length=7)

    is_profession = models.BooleanField(default=False)

    def __str__(self):
        return f"Tag {self.keyword}"


class Company(models.Model):
    name = models.CharField(max_length=127)

    description = models.TextField()

    has_access = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)


class Contact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=127)
    image = models.ImageField(upload_to="contacts/")

    telephone = models.CharField(max_length=127, blank=True)
    email = models.CharField(max_length=127, blank=True)

    def __str__(self):
        return f"Contact[{self.id}] {self.full_name} of {self.company.name}"


class User(AbstractUser):
    class UserType(models.TextChoices):
        STUDENT = "student"
        COMPANY = "company"

    user_type = models.CharField(choices=UserType.choices, max_length=15)

    subtitle = models.CharField(max_length=17, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)

    interest_tags = models.ManyToManyField(Tag, related_name="user_required_skills", null=True, blank=True)
    skills = models.ManyToManyField(Tag, related_name="user_skills", null=True, blank=True)


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    isu = models.CharField(max_length=1024)

    course = models.IntegerField()
    qualification_name = models.CharField(max_length=17)
    specialization_name = models.CharField(max_length=63)
    faculty_name = models.CharField(max_length=31)

    is_public = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"StudentProfile[{self.id}] {self.isu} {self.user.first_name}"


class Project(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)

    image = models.ImageField(upload_to="projects/")

    name = models.CharField(max_length=127)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="project_tags")

    required_skills = models.ManyToManyField(Tag, related_name="project_required_skills")
    responses = models.ManyToManyField(StudentProfile)

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Project[{self.id}] {self.name} of {self.company.name}"
