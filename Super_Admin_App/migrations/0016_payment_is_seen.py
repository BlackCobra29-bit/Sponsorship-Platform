# Generated by Django 5.1.1 on 2024-10-17 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Super_Admin_App', '0015_alter_payment_sponsor'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
    ]
