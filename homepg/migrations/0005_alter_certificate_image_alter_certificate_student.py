# Generated by Django 5.0.3 on 2024-04-01 18:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepg', '0004_remove_certificate_description_certificate_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='image',
            field=models.ImageField(null=True, upload_to='Certificates/'),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='student',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='homepg.student'),
        ),
    ]
