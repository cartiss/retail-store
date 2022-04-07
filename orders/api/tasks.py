from django.core.mail import EmailMultiAlternatives

from orders import settings
from orders.celery import app


@app.task
def send_email(key, email):
    msg = EmailMultiAlternatives(
        f"Password Reset Token for {email}",
        key,
        settings.EMAIL_HOST_USER,
        [email]
    )
    msg.send()