from django.db import models
from django.contrib.auth.models import AbstractUser
from django_lifecycle import LifecycleModel, hook, AFTER_UPDATE, AFTER_CREATE

from core.celery import send_email, send_project_publication


class Tag(models.Model):
    """ Skills or Professions """
    keyword = models.CharField(max_length=127)
    color = models.CharField(max_length=7)

    intext_match = models.CharField(max_length=1023, help_text="keywords separated by ';' symbol", blank=True)

    is_profession = models.BooleanField(default=False)

    def __str__(self):
        return f"Tag {self.keyword}"


class Company(models.Model):
    name = models.CharField(max_length=127)
    description = models.TextField()
    image = models.ImageField(upload_to="companies", null=True)

    interest_tags = models.ManyToManyField(Tag, related_name="company_required_skills", blank=True)
    skills = models.ManyToManyField(Tag, related_name="company_scope", blank=True)

    has_access = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Company[{self.id}] {self.name}"


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
    company = models.OneToOneField(Company, on_delete=models.CASCADE, null=True, blank=True)

    interest_tags = models.ManyToManyField(Tag, related_name="user_required_skills", blank=True)
    skills = models.ManyToManyField(Tag, related_name="user_skills", blank=True)


class StudentProfile(LifecycleModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    isu = models.CharField(max_length=1024)

    description = models.TextField()

    image = models.ImageField(upload_to="students/", null=True, blank=True)

    course = models.IntegerField()
    qualification_name = models.CharField(max_length=17)
    specialization_name = models.CharField(max_length=63)
    faculty_name = models.CharField(max_length=31)

    is_public = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"StudentProfile[{self.id}] {self.isu} {self.user.first_name}"

    @hook(AFTER_CREATE)
    def create_company(self):
        self.user.company = Company.objects.create(
            name=f"???????????????? ????????????????",
            description=f"???????????????? ???? {self.user.first_name}"
        )
        self.user.save()


class Project(LifecycleModel):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)

    image = models.ImageField(upload_to="projects/")
    name = models.CharField(max_length=127)
    description = models.TextField()

    tags = models.ManyToManyField(Tag, related_name="project_tags")
    required_skills = models.ManyToManyField(Tag, related_name="project_required_skills")
    team = models.ManyToManyField(StudentProfile)

    is_verified = models.BooleanField(default=False)

    @hook(AFTER_CREATE)
    def on_accepted(self):
        send_project_publication.delay(self.id)

    def __str__(self):
        return f"Project[{self.id}] {self.name} of {getattr(self.company, 'name', 'unknown')}"


class CrowdFunding(LifecycleModel):
    project = models.OneToOneField(Project, on_delete=models.SET_NULL, null=True, blank=True)

    goal = models.IntegerField()
    current = models.IntegerField()

    def __str__(self):
        return f"CrowdFunding[{self.id}]"

    @hook(AFTER_CREATE)
    def on_publish(self):
        send_email.delay(self.project.company.user.email, f"????????????????????, ???? ?????????????? ?????????????? ???????? ?????????????? ?????? ?????????????? {self.project.name}!")


class CrowdFundingDonation(LifecycleModel):
    crowdfunding = models.ForeignKey(CrowdFunding, on_delete=models.CASCADE)
    amount = models.IntegerField()

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    @hook(AFTER_CREATE)
    def on_donation(self):
        self.crowdfunding.current += self.amount
        self.crowdfunding.save()

        send_email.delay(self.crowdfunding.project.company.user.email, f"?????? ???????????? {self.crowdfunding.project.name} ???????????????????? ???? {self.amount} ????????????!")


class StudentRequest(LifecycleModel):
    class StudentRequestState(models.TextChoices):
        OPEN = "open"
        ACCEPTED = "accepted"
        REJECTED = "rejected"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)

    initiator = models.CharField(choices=User.UserType.choices, max_length=15, default=User.UserType.STUDENT)

    datetime = models.DateTimeField(auto_now=True)
    state = models.CharField(StudentRequestState.choices, default=StudentRequestState.OPEN, max_length=15)

    @hook(AFTER_UPDATE, when="state", was=StudentRequestState.OPEN, is_now=StudentRequestState.ACCEPTED)
    def on_accepted(self):
        if self.initiator == User.UserType.COMPANY:
            send_email.delay(
                self.student.user.email,
                f"????????????????????! ?????? ?????????????????????????? ???????????????? {self.company.name} ?????? ?????????????? {self.project.name}. ??????????????????."
            )
        else:
            send_email.delay(
                self.company.user.email,
                f"?????????????? {self.student.user.first_name} ?????????? ?????????????????????????? ?? ?????????????? {self.project.nameg}"
            )

    @hook(AFTER_UPDATE, when="state", was=StudentRequestState.OPEN, is_now=StudentRequestState.REJECTED)
    def on_rejected(self):
        if self.initiator == User.UserType.COMPANY:
            send_email.delay(
                self.student.user.email,
                f"?? ??????????????????, ???????????????? {self.company.name} ???? ?????????????????????????? ???????? ?????????????????????? ?????? ?????????????? {self.project.name}."
            )
        else:
            send_email.delay(
                self.company.user.email,
                f"?? ??????????????????, ?????????????? {self.student.user.first_name} ???????? ???? ?????????? ?????????????????????????? ?????????? ?? ?????????????? {self.project.name}."
            )

    def __str__(self):
        return f"StudentRequest[{self.id}] {self.company_id} {self.student.isu}"


class Review(LifecycleModel):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now=True)
    review = models.TextField()

    @hook(AFTER_CREATE)
    def on_publish(self):
        send_email.delay(
            self.student.user.email,
            f"?????? ???????????????? ???????????? ???????????????? {self.company.name}!"
        )


class CompanyStudentEmotion(LifecycleModel):
    class CompanyEmotion(models.TextChoices):
        LIKE = "like"
        DISLIKE = "dislike"

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    emotion = models.CharField(choices=CompanyEmotion.choices, max_length=15)

    @hook(AFTER_CREATE, when="emotion", is_now="like")
    def on_like(self):
        send_email(
            self.student.user.email,
            f"???? ?????????????????????? ???????????????? {self.company.name}! ?????????? ?????????? ?????????? ?? ???????? ??????????????????? ;)"
        )
