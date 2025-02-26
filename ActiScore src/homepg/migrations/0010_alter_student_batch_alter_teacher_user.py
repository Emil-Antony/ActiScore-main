# Generated by Django 5.0.3 on 2024-04-10 11:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepg', '0009_alter_student_batch_alter_teacher_batch_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='batch',
            field=models.CharField(choices=[('9', '9'), ('10', '10'), ('11', '11'), ('12-a', '12-a'), ('12-b', '12-b')], default='9', max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
