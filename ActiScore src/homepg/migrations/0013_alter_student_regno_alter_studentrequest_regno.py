# Generated by Django 5.0.3 on 2024-04-27 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepg', '0012_customuser_verified_studentrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='regno',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='studentrequest',
            name='regno',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
    ]
