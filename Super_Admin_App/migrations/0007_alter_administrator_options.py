# Generated by Django 5.1.1 on 2024-09-17 18:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Super_Admin_App', '0006_alter_familylist_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='administrator',
            options={'ordering': ['-created_at'], 'verbose_name_plural': 'Administrators'},
        ),
    ]
