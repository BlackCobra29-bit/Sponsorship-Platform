# Generated by Django 5.1.1 on 2025-01-01 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Super_Admin_App', '0023_delete_familylisttig'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailCredential',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_host_user', models.EmailField(max_length=254)),
                ('email_host_password', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'AppEmail',
            },
        ),
        migrations.AlterField(
            model_name='monthlyamount',
            name='amount',
            field=models.DecimalField(decimal_places=2, default='30.00', max_digits=10, verbose_name='Monthly Amount'),
        ),
    ]
