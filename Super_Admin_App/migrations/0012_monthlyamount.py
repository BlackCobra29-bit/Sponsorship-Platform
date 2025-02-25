# Generated by Django 5.1.1 on 2024-09-29 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Super_Admin_App', '0011_alter_familyimage_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Monthly Amount')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Monthly Amount',
                'verbose_name_plural': 'Monthly Amounts',
                'ordering': ['-created_at'],
            },
        ),
    ]
