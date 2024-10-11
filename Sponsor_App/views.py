import stripe
import logging
from django.views import View
from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from Messaging.models import Message
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import UpdateView
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from Sponsor_App.models import SponosrAccount
from Super_Admin_App.models import FamilyList, MonthlyAmount
from .mixins import MessageContextMixin
from Super_Admin_App.forms import UserModelForm, CustomPasswordChangeForm


logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


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
        context["messages_list"] = Message.objects.filter(
            receiver=self.request.user
        ).order_by("-timestamp")
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
        messages.success(self.request, "Account information updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating the account details.")
        return super().form_invalid(form)


class PasswordUpdateView(SuperAdminRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    login_url = "/login-page"
    template_name = "password_change_form.html"
    success_url = reverse_lazy("sponsor-home-page")

    def form_valid(self, form):
        messages.success(self.request, "Password updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating the Password.")
        return super().form_invalid(form)


class StripeCheckoutView(SuperAdminRequiredMixin, View):
    
    login_url = "/login-page"

    def get(self, request, family_id, *args, **kwargs):
        try:
            # Retrieve the monthly amount and convert it to cents
            monthly_amount = MonthlyAmount.objects.first().amount
            amount_in_cents = int(monthly_amount * 100)
            selected_family = get_object_or_404(FamilyList, pk=family_id)

            # Create the Stripe session
            stripe_session = stripe.checkout.Session.create(
                payment_method_types=[
                    "card",
                    "au_becs_debit",
                ],
                line_items=[
                    {
                        "price_data": {
                            "currency": "aud",
                            "unit_amount": amount_in_cents,
                            "product_data": {
                                "name": selected_family.family_name,
                                # Uncomment the line below for production to use real images
                                # "images": [selected_family.images.first().photo.url] if selected_family.images.exists() else []
                                "images": [
                                    "https://www.ippf.org/sites/default/files/2022-05/ippf_humanitarian_tigray_crisis_sudan_2022_89763_ippf_hannah_maule-ffinch_sudan_ippf.jpg"
                                ],
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                customer_email=request.user.email,
                success_url=request.build_absolute_uri(reverse("payment-success")),
                cancel_url=request.build_absolute_uri(reverse("payment-cancel")),
                metadata={
                    "family_id": selected_family.id,
                    "sponsor_id": request.user.id,
                },
            )

            return redirect(stripe_session.url)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return redirect("family-list-page")
        except Exception as e:
            logger.error(f"Error during checkout: {str(e)}")
            return redirect("family-list-page")

@method_decorator(csrf_exempt, name='dispatch')
class WebhookManagerView(View):

    def post(self, request, *args, **kwargs):
        stripe_payload = request.body.decode('utf-8')
        signature_header = request.META.get("HTTP_STRIPE_SIGNATURE", None)
        if not signature_header:
            return JsonResponse({"error": "Missing signature"}, status=400)

        try:
            stripe_event = stripe.Webhook.construct_event(
                stripe_payload, signature_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return JsonResponse({"error": "Invalid payload"}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({"error": "Invalid signature"}, status=400)

        if stripe_event["type"] == "checkout.session.completed":
            stripe_session = stripe_event["data"]["object"]
            logger.info("Checkout Session Completed!")
            # self.manage_checkout_session(stripe_session)

        return JsonResponse({"status": "success"})

    # def manage_checkout_session(self, stripe_session):
    #     tutorial_id = stripe_session["metadata"]["tutorial_id"]
    #     user_id = stripe_session["metadata"]["buyer_id"]

    #     try:
    #         user = User.objects.get(id=user_id)
    #     except User.DoesNotExist:
    #         logger.error(f"User with ID {user_id} not found.")
    #         return

    #     tutorial = get_object_or_404(tutorials, pk=tutorial_id)
    #     purchaser = Purchaser.objects.create(user=user)
    #     purchaser.purchased_courses.set([tutorial])

class PaymentSuccessView(SuperAdminRequiredMixin, TemplateView):
    login_url = "/login-page"
    template_name = "payment_success.html"


class PaymentCancelView(SuperAdminRequiredMixin, TemplateView):
    login_url = "/login-page"
    template_name = "payment_cancel.html"
