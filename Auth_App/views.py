from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from Sponsor_App.models import SponosrAccount
from django.http import JsonResponse
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.contrib.auth.mixins import LoginRequiredMixin


# Login View (CBV)
class LoginView(TemplateView):
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("admin-dashboard" if request.user.is_superuser else "sponsor-home-page")
        
        # Generate CAPTCHA for GET requests
        captcha_key = CaptchaStore.generate_key()
        captcha_image = captcha_image_url(captcha_key)

        return self.render_to_response({
            "captcha_image": captcha_image,
            "captcha_key": captcha_key
        })

    def post(self, request, *args, **kwargs):
        username = request.POST.get("login_username")
        password = request.POST.get("login_password")
        captcha_key = request.POST.get("captcha_0")  # Captcha key
        captcha_value = request.POST.get("captcha_1")  # User-entered captcha text

        # Validate CAPTCHA
        try:
            captcha_obj = CaptchaStore.objects.get(hashkey=captcha_key)
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
            return redirect("admin-dashboard" if user_auth.is_superuser else "sponsor-home-page")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("admin-login")


# Logout View (CBV)
class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect("admin-login")


# Create Account View (CBV)
class CreateAccountView(TemplateView):
    template_name = "create_account.html"

    def post(self, request, *args, **kwargs):
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

        # Create associated SponsorAccount
        SponosrAccount.objects.create(user=user, phone_number=phone)

        # Return JSON response
        return JsonResponse(
            {"success": True, "message": "Account created successfully!"}
        )

# Forgot Password View (CBV)
class ForgotPasswordView(TemplateView):
    template_name = "forgot_password.html"