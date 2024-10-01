from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .mixins import MessageContextMixin  # Import your mixin
from Messaging.models import Message


# Custom mixin to restrict access for superusers
class SuperAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect("permission-denied")
        return super().dispatch(request, *args, **kwargs)


class SponsorHomePage(SuperAdminRequiredMixin, MessageContextMixin, TemplateView):
    template_name = "sponsor_home.html"
    login_url = "/login-page"
    redirect_field_name = "authentication_required"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unread_messages"] = Message.objects.filter(
            receiver=self.request.user, is_read=False
        )
        return context


class MySponsorshipPage(SuperAdminRequiredMixin, MessageContextMixin, TemplateView):
    template_name = "my_sponsorship.html"
    login_url = "/login-page"
    redirect_field_name = "authentication_required"


class ReceivedMessages(SuperAdminRequiredMixin, MessageContextMixin, TemplateView):
    template_name = "received_messages.html"
    login_url = "/login-page"
    redirect_field_name = "authentication_required"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages_list'] = Message.objects.filter(receiver = self.request.user)
        return context