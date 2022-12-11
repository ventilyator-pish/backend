import os
from collections import defaultdict

from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

from core.utils.coverage import coverage


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task
def send_email(email: str, body: str):
    send_mail(
        "Платформа engineers-itmo.ru",
        body,
        settings.EMAIL_HOST_USER,
        [email]
    )


@app.task
def send_project_publication(public_id: int):
    from core.models import Project, User

    project = Project.objects.get(id=public_id)
    required_skills = project.required_skills.values_list("id")

    user_interests_tags = defaultdict(list)

    for user_email, tag_id in User.objects.values_list("email", "interest_tags__id"):
        user_interests_tags[user_email].append(tag_id)

    user_coverage = {email: coverage(user_tags, required_skills) for email, user_tags in user_interests_tags}

    for email, c in user_coverage:
        if c > 0.5:
            send_email.delay(
                email,
                f"Возможно стоит обратить внимание на проект {project.name}? У вас более 50% совпадений по интересам!"
            )
