# Generated by Django 5.1.1 on 2024-10-10 16:39

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Sponsor_App', '0003_rename_admin_photo_sponosraccount_sponsor_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponosraccount',
            name='location',
            field=django_countries.fields.CountryField(default='Ethiopia', max_length=2),
            preserve_default=False,
        ),
    ]
