# Generated by Django 4.2.2 on 2023-12-03 17:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entreprise', '0004_alter_enterprise_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enterprise',
            name='sectors',
        ),
    ]