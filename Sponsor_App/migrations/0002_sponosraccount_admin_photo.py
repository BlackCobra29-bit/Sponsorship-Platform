# Generated by Django 5.1.1 on 2024-10-01 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sponsor_App', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponosraccount',
            name='admin_photo',
            field=models.ImageField(default='default.jpg', upload_to='sponsor_media'),
            preserve_default=False,
        ),
    ]
