from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(
    login_url="/login-page", redirect_field_name="authentication_required"
)
def home_page(request):

    return render(request, "sponsor_home.html")


@login_required(
    login_url="/login-page", redirect_field_name="authentication_required"
)
def my_sponsorship(request):

    return render(request, "my_sponsorship.html")
