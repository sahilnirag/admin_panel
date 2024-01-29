from django.core.mail import EmailMessage
import os
from django.conf import settings
from api.models import *

class Util:
  @staticmethod
  def send_email(data):
    email = EmailMessage(
      subject=data['subject'],
      body=data['body'],
      from_email=settings.EMAIL_HOST_USER,
      to=[data['to_email']]
    )
    email.send()




def notification(title,description,created_by,created_for):
  Notification.objects.create(
    title = title,
    description = description,
    created_by_id = created_by,
    created_for_id = created_for
    )
  