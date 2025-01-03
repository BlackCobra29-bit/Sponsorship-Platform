from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.views.generic import TemplateView, View, DeleteView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from Sponsor_App.models import SponosrAccount
from django.http import JsonResponse
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class LoginView(TemplateView):
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if self.request.GET.get("family-id"):
                logout(request)
            else:
                return redirect("admin-dashboard" if request.user.is_superuser else "sponsor-home-page")
        
        captcha_key = CaptchaStore.generate_key()
        captcha_image = captcha_image_url(captcha_key)

        return self.render_to_response({
            "captcha_image": captcha_image,
            "captcha_key": captcha_key
        })

    def post(self, request, *args, **kwargs):
        username = request.POST.get("login_username")
        password = request.POST.get("login_password")
        captcha_key = request.POST.get("captcha_0")
        captcha_value = request.POST.get("captcha_1")

        try:
            captcha_obj = CaptchaStore.objects.get(hashkey=captcha_key)
            if captcha_obj.response.lower() != captcha_value.lower():
                messages.error(request, "Invalid CAPTCHA.")
                return self.redirect_with_query_params(request)
        except CaptchaStore.DoesNotExist:
            messages.error(request, "Invalid CAPTCHA.")
            return self.redirect_with_query_params(request)

        user_auth = authenticate(request, username=username, password=password)
        if user_auth is not None:
            login(request, user_auth)

            if self.request.GET.get("family-id"):

                if request.POST.get("paymentMethod") == "card":
                    return redirect(reverse("stripe-checkout", args=[self.request.GET.get("family-id")]))

                if request.POST.get("paymentMethod") == "paypal":
                    return redirect(reverse("paypal-checkout", args=[self.request.GET.get("family-id")]))
            else:
                return redirect("admin-dashboard" if user_auth.is_superuser else "sponsor-home-page")
        else:
            messages.error(request, "Invalid username or password.")
            return self.redirect_with_query_params(request)

    def redirect_with_query_params(self, request):
        return redirect(f"{reverse('admin-login')}?{request.GET.urlencode()}")


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect("admin-login")


class ForgotPasswordView(TemplateView):
    template_name = "forgot_password.html"


class DeleteAccountView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("admin-login")

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Your account has been deleted successfully.')
        return super().delete(request, *args, **kwargs)