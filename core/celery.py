import os

from celery import Celery
from django.core.mail import send_mail
from django.conf import settings


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
    pass
