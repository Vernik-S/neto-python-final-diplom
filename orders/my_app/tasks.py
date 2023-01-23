from orders.celery import app
from django.core.mail import EmailMultiAlternatives


@app.task
def send_mail(title, message, from_, to_):
    msg = EmailMultiAlternatives(
        # title:
        title,
        # message:
        message,
        # from:
        from_,
        # to:
        to_
    )
    msg.send()

