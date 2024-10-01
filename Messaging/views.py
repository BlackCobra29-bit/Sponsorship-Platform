from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from Messaging.models import Message
from django.http import JsonResponse


# Mail Page View (CBV)
class MailPageView(LoginRequiredMixin, TemplateView):
    login_url = "/login-page"
    redirect_field_name = "authentication_required"
    template_name = "mail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages_list'] = Message.objects.all()
        return context

# Compose Page View (CBV)
class ComposePageView(LoginRequiredMixin, CreateView):
    login_url = "/login-page"
    redirect_field_name = "authentication_required"
    template_name = "compose.html"
    model = Message
    fields = ["sender", "receiver", "subject", "message"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the 'receiver' based on GET request
        username = self.request.GET.get("sponsor_account")
        user = get_object_or_404(User, username=username)
        context["user"] = user
        return context

    def post(self, request, *args, **kwargs):
        username = self.request.GET.get("sponsor_account")
        receiver_user = get_object_or_404(User, username=username)

        Message.objects.create(
            sender=request.user,
            receiver=receiver_user,
            subject=request.POST.get("subject"),
            message=request.POST.get("content"),
        )

        return JsonResponse(
            {"success": True, f"message": "Message sent successfully!!"}
        )