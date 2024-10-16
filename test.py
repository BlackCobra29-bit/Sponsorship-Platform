import os
import django

# Set up Django settings environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "Hidrina_Website.settings")  # Replace with your project name

# Initialize Django
django.setup()

import django.conf
from django.core.mail import send_mail
from django.conf import settings

# Send email
send_mail(
    'Subject here',
    'Here is the message.',
    settings.EMAIL_HOST_USER,
    ['eminemmerne@gmail.com'],
    fail_silently=False,
)

print("Email sent successfully!")
