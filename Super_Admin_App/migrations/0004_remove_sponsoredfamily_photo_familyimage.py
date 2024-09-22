# Generated by Django 5.1.1 on 2024-09-16 13:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Super_Admin_App', '0003_alter_administrator_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sponsoredfamily',
            name='photo',
        ),
        migrations.CreateModel(
            name='FamilyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='family_photos/')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='Super_Admin_App.sponsoredfamily')),
            ],
        ),
    ]