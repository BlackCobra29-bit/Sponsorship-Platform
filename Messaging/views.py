from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.
def MailPage(request):

    return render(request, 'mail.html')

def ComposePage(request):

    return render(request, 'compose.html')