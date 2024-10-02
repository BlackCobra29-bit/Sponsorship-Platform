from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from Messaging.models import Message
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import UpdateView
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
# custom mixins
from .mixins import MessageContextMixin
# import UserModelForm from Super_Admin_App
from Super_Admin_App.forms import UserModelForm, CustomPasswordChangeForm


# Custom mixin to restrict access for superusers
class SuperAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect("admin-login")
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
        context['messages_list'] = Message.objects.filter(receiver = self.request.user).order_by("-timestamp")
        return context
    
class ViewMessage(SuperAdminRequiredMixin, MessageContextMixin, TemplateView):
    template_name = "view_message.html"
    login_url = "/login-page"
    redirect_field_name = "authentication_required"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message_id = self.request.GET.get("message_id")
        message = get_object_or_404(Message, pk=message_id)
        
        if not message.is_read:
            message.is_read = True
            message.save()
        
        context["message"] = message
        return context
    
# User Update View (CBV)
class UserUpdateView(SuperAdminRequiredMixin, UpdateView):
    model = User
    login_url = "/login-page"
    form_class = UserModelForm
    template_name = "account_update.html"
    success_url = reverse_lazy("sponsor-home-page")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.object
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Account information updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the account details.')
        return super().form_invalid(form)
    
class PasswordUpdateView(SuperAdminRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    login_url = "/login-page"
    template_name = 'password_change_form.html'
    success_url = reverse_lazy('sponsor-home-page')

    def form_valid(self, form):
        messages.success(self.request, 'Password updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the Password.')
        return super().form_invalid(form)
