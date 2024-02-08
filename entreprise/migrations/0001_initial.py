# Generated by Django 4.2.2 on 2024-02-08 10:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import entreprise.models


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
            bases=(models.Model, entreprise.models.ModelBasic),
        ),
        migrations.CreateModel(
            name='EconomicSector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sectorname', models.CharField(default='', max_length=255)),
                ('sectordesciption', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Enterprise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(default='nothin@gmail.com', max_length=255, verbose_name='email adress')),
                ('name', models.CharField(max_length=255)),
                ('ifu', models.CharField(default=' ', max_length=255)),
                ('rcm', models.CharField(default=' ', max_length=255)),
                ('director_card_id', models.CharField(default=' ', max_length=255)),
                ('director_card_file', models.ImageField(default='default_rccm.png', upload_to='statics/')),
                ('rccm_file', models.ImageField(default='default.png', upload_to='statics/')),
                ('director_card_type', models.CharField(choices=[('PASSPORT', 'Passport'), ('CNI', 'CNI')], default='CNI', max_length=255)),
                ('director_lastname', models.CharField(default='String', max_length=255)),
                ('director_firstname', models.CharField(default='String', max_length=255)),
                ('phone', models.CharField(default='String', max_length=255)),
                ('is_approved', models.BooleanField(default=False)),
                ('logo', models.ImageField(default='default_logo.png', upload_to='statics/')),
                ('status', models.IntegerField(default=0)),
                ('description', models.CharField(default='String', max_length=255)),
                ('adress', models.CharField(default='String', max_length=255)),
                ('request_to_use', models.CharField(default=' ', max_length=255)),
                ('country', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='entreprise.country')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('sectors', models.ManyToManyField(default=1, to='entreprise.economicsector')),
            ],
        ),
        migrations.CreateModel(
            name='EnterpriseAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('job', models.CharField(max_length=100)),
                ('job_description', models.CharField(max_length=100)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
                ('enterprises', models.ManyToManyField(to='entreprise.enterprise')),
            ],
        ),
        migrations.CreateModel(
            name='EnterpriseScheduleEnter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_at', models.DateField()),
                ('end_at', models.DateField()),
                ('task_to_do', models.TextField()),
                ('comment', models.TextField()),
            ],
            bases=(models.Model, entreprise.models.ModelBasic),
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
                ('code', models.CharField(max_length=255, unique=True)),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.CharField(max_length=255)),
                ('check_security_code', models.BooleanField(default=False)),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterprise')),
            ],
        ),
        migrations.CreateModel(
            name='Qr',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_current', models.BooleanField(default=False)),
                ('qr_code', models.CharField(max_length=255)),
                ('qr_image', models.ImageField(default='default.png', upload_to='statics/')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
            ],
        ),
        migrations.CreateModel(
            name='PermissionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('start_at', models.DateTimeField()),
                ('end_at', models.DateTimeField()),
                ('is_approved', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterprise')),
            ],
            bases=(models.Model, entreprise.models.ModelBasic),
        ),
        migrations.CreateModel(
            name='ModifyEmployeeDataRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_modification', models.CharField(choices=[('PICTURE', 'Picture'), ('QR_CODE', 'QR Code'), ('SECURITY_CODE', 'Security Code')], default='picture', max_length=20)),
                ('new_data', models.CharField(max_length=255)),
                ('document', models.FileField(blank=True, null=True, upload_to='employee_data_requests/')),
                ('reason', models.TextField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterprise')),
            ],
            bases=(models.Model, entreprise.models.ModelBasic),
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(choices=[('ANNUAL_LEAVE', 'Annual Leave'), ('SICK_LEAVE', 'Sick Leave'), ('UNPAID_LEAVE', 'Unpaid Leave')], default='Sick Leave', max_length=20)),
                ('reason', models.TextField()),
                ('start_at', models.DateField()),
                ('end_at', models.DateField()),
                ('is_approuve', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterprise')),
            ],
            bases=(models.Model, entreprise.models.ModelBasic),
        ),
        migrations.CreateModel(
            name='Face',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_main', models.BooleanField(default=False)),
                ('status', models.BooleanField(default=False)),
                ('face_file', models.FileField(default='default.png', upload_to='statics/')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
            ],
        ),
        migrations.CreateModel(
            name='EnterpriseSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_at', models.DateField()),
                ('end_at', models.DateField()),
                ('task_to_do', models.TextField()),
                ('comment', models.TextField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterprise')),
            ],
            bases=(models.Model, entreprise.models.ModelBasic),
        ),
        migrations.CreateModel(
            name='EnterpriseAdminRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterprise')),
                ('entreprise_admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterpriseadmin')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.role')),
            ],
        ),
        migrations.AddField(
            model_name='enterpriseadmin',
            name='roles',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='entreprise.role'),
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
                ('date_add_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.room')),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='enterprise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterprise'),
        ),
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='DocumentCopyRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(choices=[('WORK_CERTIFICATE', 'Work Certificate'), ('EMPLOYMENT_CONTRACT', 'Employment Contract'), ('PAYSLIP', 'Payslip')], default='Work Certificate', max_length=20)),
                ('comment', models.TextField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterprise')),
            ],
            bases=(models.Model, entreprise.models.ModelBasic),
        ),
        migrations.CreateModel(
            name='BreakRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('start_at', models.DateTimeField()),
                ('end_at', models.DateTimeField()),
                ('is_approved', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterprise')),
            ],
            bases=(models.Model, entreprise.models.ModelBasic),
        ),
        migrations.CreateModel(
            name='AccesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_mode', models.CharField(choices=[('Qr code', 'Qr Code'), ('Security code', 'Code de Sécurity'), ('Face', 'Visage')], default='Visage', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.employee')),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.enterprise')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entreprise.room')),
            ],
        ),
    ]
