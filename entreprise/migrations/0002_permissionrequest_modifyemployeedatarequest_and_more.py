# Generated by Django 4.2.2 on 2024-01-28 17:00

from django.db import migrations, models
import django.db.models.deletion
import entreprise.models


class Migration(migrations.Migration):

    dependencies = [
        ('entreprise', '0001_initial'),
    ]

    operations = [
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
    ]
