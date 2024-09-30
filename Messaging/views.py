from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

# Mail Page View (CBV)
class MailPageView(LoginRequiredMixin, TemplateView):
    login_url = "/login-page"
    redirect_field_name = "authentication_required"
    template_name = 'mail.html'

# Compose Page View (CBV)
class ComposePageView(LoginRequiredMixin, TemplateView):
    login_url = "/login-page"
    redirect_field_name = "authentication_required"
    template_name = 'compose.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the 'username' from the query parameters
        username = self.request.GET.get('sponsor_account')  # Use 'username' as your key
        user = get_object_or_404(User, username=username)
        context['user'] = user  # Pass the user to the template context
        return context