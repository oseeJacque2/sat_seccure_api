# Generated by Django 4.2.2 on 2023-12-03 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entreprise', '0003_enterprise_director_firstname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enterprise',
            name='email',
            field=models.EmailField(default='nothin@gmail.com', max_length=255, verbose_name='email adress'),
        ),
    ]