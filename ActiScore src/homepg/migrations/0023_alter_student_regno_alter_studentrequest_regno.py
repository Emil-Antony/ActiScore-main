# Generated by Django 5.0.3 on 2024-05-07 12:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepg', '0022_alter_activity_certificate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='regno',
            field=models.CharField(blank=True, max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='Enter a valid registration number.', regex='^(aik|AIK)\\d{2}(cs|CS)\\d{3}$')]),
        ),
        migrations.AlterField(
            model_name='studentrequest',
            name='regno',
            field=models.CharField(blank=True, max_length=20, unique=True, validators=[django.core.validators.RegexValidator(message='Enter a valid registration number.', regex='^(aik|AIK)\\d{2}(cs|CS)\\d{3}$')]),
        ),
    ]
