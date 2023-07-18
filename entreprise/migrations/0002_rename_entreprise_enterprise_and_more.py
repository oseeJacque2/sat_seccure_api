# Generated by Django 4.2.2 on 2023-07-10 13:07

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entreprise', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Entreprise',
            new_name='Enterprise',
        ),
        migrations.RenameModel(
            old_name='EntrepriseAdmin',
            new_name='EnterpriseAdmin',
        ),
        migrations.RenameModel(
            old_name='EntrepriseAdminRole',
            new_name='EnterpriseAdminRole',
        ),
        migrations.RenameField(
            model_name='room',
            old_name='entreprise',
            new_name='enterprise',
        ),
    ]
