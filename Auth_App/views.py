import random
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from Sponsor_App.models import SponosrAccount
from django.http import JsonResponse
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore


def render_login_page(request):
    if request.user.is_authenticated:
        return redirect(
            "admin-dashboard" if request.user.is_superuser else "sponsor-home-page"
        )

    if request.method == "POST":
        username = request.POST.get("login_username")
        password = request.POST.get("login_password")
        captcha_key = request.POST.get("captcha_0")  # Captcha key
        captcha_value = request.POST.get("captcha_1")  # User-entered captcha text

        # Validate CAPTCHA
        try:
            captcha_obj = CaptchaStore.objects.get(hashkey=captcha_key)
            # Case-insensitive comparison
            if captcha_obj.response.lower() != captcha_value.lower():
                messages.error(request, "Invalid CAPTCHA.")
                return redirect("admin-login")
        except CaptchaStore.DoesNotExist:
            messages.error(request, "Invalid CAPTCHA.")
            return redirect("admin-login")

        # Authenticate user
        user_auth = authenticate(request, username=username, password=password)
        if user_auth is not None:
            login(request, user_auth)
            return redirect(
                "admin-dashboard" if user_auth.is_superuser else "sponsor-home-page"
            )
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("admin-login")

    # Generate CAPTCHA for GET requests
    captcha_key = CaptchaStore.generate_key()
    captcha_image = captcha_image_url(captcha_key)

    return render(request, "login.html", {"captcha_image": captcha_image, "captcha_key": captcha_key})

def render_logout(request):

    logout(request)

    return redirect("admin-login")


def render_create_account_page(request):
    if request.method == "POST":
        # Get the form inputs
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": "Username already taken. Please choose another.",
                }
            )

        # Create the user
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=make_password(password),  # Password is hashed for security
        )

        # Create associated SponosrAccount
        SponosrAccount.objects.create(user=user, phone_number=phone)

        # Return JSON response
        return JsonResponse(
            {"success": True, "message": "Account created successfully!"}
        )

    return render(request, "create_account.html")


def render_forgot_password_page(request):

    return render(request, "forgot_password.html")
