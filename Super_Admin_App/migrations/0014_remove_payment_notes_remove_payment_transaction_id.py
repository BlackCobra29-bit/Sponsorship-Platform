# Generated by Django 5.1.1 on 2024-10-12 06:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Super_Admin_App', '0013_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='transaction_id',
        ),
    ]
