from django.db import models

from account.models import Custom_User


# Create your models here.

class SystemAdmin (models.Model):
    user_admin = models.ForeignKey(Custom_User, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.user_admin}"