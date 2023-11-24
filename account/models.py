from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils import timezone

SEXE_CHOICES=(
    ("HOMME", "HOMME"),
    ("FEMMME", "FEMME"),
    ("AUCUN", "AUCUN")
)



class MyUserManger(BaseUserManager):
    def create_user(self, email, firstname=" String",lastname="String", password=None, birth_date=timezone.now(), sexe='', adresse='', description='', profession='', telephone=''):
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            birth_date=birth_date,
            firstname= firstname, 
            lastname = lastname,
            adresse=adresse,
            description=description,
            profession=profession,
            telephone=telephone,
            sexe=sexe

        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,firstname,lastname, password=None, birth_date=timezone.now(), sexe='', adresse='', description='', profession='', telephone=''):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(
            email,
            firstname = firstname, 
            lastname = lastname,
            password=password,
            birth_date=birth_date,
            sexe=sexe,
            adresse=adresse,
            description=description,
            profession=profession,
            telephone=telephone

        )
        user.is_admin = True
        user.save(using=self._db)
        return user



class Custom_User(AbstractUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email adress',
                              max_length=255,
                              unique=True
                              )
    lastname = models.CharField(max_length=255,default="String")
    name = models.CharField(max_length=255, default="String")
    firstname = models.CharField(max_length=255,default="String")
    username = models.CharField(max_length=255,default="String")
    sexe = models.CharField(max_length=15, choices=SEXE_CHOICES, default="AUCUN")
    telephone = models.CharField(max_length=20, default="")
    picture = models.ImageField(default="default.png",  upload_to='statics/')

    birth_date = models.DateField(default=timezone.now)
    adresse= models.CharField(max_length=200, default="")
    description = models.CharField(max_length=200, default="Aucune description")
    profession = models.CharField(max_length=200, default="Aucune rofession")
    date_created_at = models.DateTimeField(auto_now_add=True)
    date_updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_validate = models.BooleanField(default=False)


    objects = MyUserManger()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    def __str__(self):
        return f"{self.lastname} {self.firstname}"

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin




class ActivationCode(models.Model):
    user = models.OneToOneField(Custom_User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        expiration_time = timezone.now() - timezone.timedelta(minutes=10)
        return self.created_at < expiration_time