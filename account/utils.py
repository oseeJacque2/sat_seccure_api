import os
import random
import string
from django.core.mail import EmailMessage


class Util:
    @staticmethod
    def send_mail(data):
        email=EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=os.environ.get("EMAIL_FROM"),
            to=[data['to_email']]
        )
        email.send() 

    @staticmethod
    def generate_activation_code(length=6):
        """
        Generate a random activation code with the specified length.
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))
