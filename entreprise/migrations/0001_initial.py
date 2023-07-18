# Generated by Django 4.2.2 on 2023-07-04 16:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('continent', models.CharField(choices=[('AFRIQUE', 'Afrique'), ('EUROPE', 'Europe'), ('AMERIQUE', 'Amerique'), ('OCEANIE', 'Océanie'), ('ASIE', 'Asie')], max_length=255)),
                ('indicatif', models.CharField(max_length=255)),
                ('iso_code', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Entreprise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('ifu', models.CharField(max_length=255)),
                ('rccm', models.CharField(max_length=255)),
                ('dirrector_card_id', models.CharField(max_length=255)),
                ('dirrector_card_file', models.ImageField(default='default.png', upload_to='')),
                ('dirrector_card_type', models.CharField(choices=[('PASSPORT', 'Passport'), ('CNI', 'CNI')], max_length=255)),
                ('director_lastname', models.CharField(max_length=255)),
                ('director_firstname', models.CharField(max_length=255)),
                ('is_approved', models.BooleanField(default=False)),
                ('logo', models.ImageField(default='default.png', upload_to='')),
                ('description', models.CharField(max_length=255)),
                ('request_to_use', models.CharField(max_length=255)),
                ('country', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='entreprise.country')),
            ],
        ),
        migrations.CreateModel(
            name='EntrepriseAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('job', models.CharField(max_length=100)),
                ('job_description', models.CharField(max_length=100)),
                ('is_creator', models.BooleanField(default=False)),
                ('enterprises', models.ManyToManyField(to='entreprise.entreprise')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('ADMINISTRATION', 'Administration'), ('SOFTWARE', 'Software')], default='Administration', max_length=255)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SecurityCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_current', models.BooleanField(default=False)),
                ('code', models.CharField(max_length=255)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.CharField(max_length=255)),
                ('check_security_code', models.BooleanField(default=False)),
                ('entreprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.entreprise')),
            ],
        ),
        migrations.CreateModel(
            name='Qr',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_current', models.BooleanField(default=False)),
                ('qr_code', models.CharField(max_length=255)),
                ('qr_image', models.ImageField(default='default.png', upload_to='')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Face',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_main', models.BooleanField(default=False)),
                ('status', models.BooleanField(default=False)),
                ('face_file', models.ImageField(default='default.png', upload_to='')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
            ],
        ),
        migrations.CreateModel(
            name='EntrepriseAdminRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('entreprise_admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.entrepriseadmin')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.role')),
            ],
        ),
        migrations.AddField(
            model_name='entrepriseadmin',
            name='roles',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='entreprise.role'),
        ),
        migrations.AddField(
            model_name='entrepriseadmin',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='EmployeeStatusLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('employee_log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.room')),
            ],
        ),
    ]
