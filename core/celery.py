from django.core.mail import send_mail
from django.conf import settings


def send_email(email: str, body: str):
    send_mail(
        "Платформа engineers-itmo.ru",
        body,
        settings.EMAIL_HOST_USER,
        [email]
    )


def send_project_publication(public_id: int):
    pass
