import os
import uuid
import stripe
import logging
from django.db.models import Sum
from django.views import View
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.ipn.models import PayPalIPN
from .models import SponsorFamilyRelation
from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from Messaging.models import Message
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import UpdateView, ListView
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from Sponsor_App.models import SponsorFamilyRelation
from Super_Admin_App.models import FamilyList, MonthlyAmount, Payment
from .mixins import MessageContextMixin, SponsorPaymentNotificationMixin
from Super_Admin_App.forms import UserModelForm, CustomPasswordChangeForm
from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.forms import PayPalPaymentsForm

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

class SuperAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            messages.error(request, "Admin accounts cannot be used for sponsorship.")
            return redirect("admin-login")
        return super().dispatch(request, *args, **kwargs)

class SponsorHomePage(SuperAdminRequiredMixin, SponsorPaymentNotificationMixin, MessageContextMixin, TemplateView):
    template_name = "sponsor_home.html"
    login_url = "/login-page"
    redirect_field_name = "authentication_required"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unread_messages"] = Message.objects.filter(
            receiver=self.request.user, is_read=False
        )
        sponsored_relations = SponsorFamilyRelation.objects.filter(sponsor=self.request.user)
        context["count_family_sponsored"] = sponsored_relations.count() if sponsored_relations.exists() else 0
        total_amount_paid = Payment.objects.filter(sponsor=self.request.user).aggregate(total=Sum('amount'))['total'] or 0
        context["total_amount_paid"] = total_amount_paid
        return context

class MySponsorshipPage(SuperAdminRequiredMixin, SponsorPaymentNotificationMixin, MessageContextMixin, TemplateView):
    template_name = "my_sponsorship.html"
    login_url = "/login-page"
    redirect_field_name = "authentication_required"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unread_messages"] = Message.objects.filter(
            receiver=self.request.user, is_read=False
        )
        sponsored_relations = SponsorFamilyRelation.objects.filter(sponsor=self.request.user)
        context["sponsored_families"] = [relation.family for relation in sponsored_relations]
        return context
    
class PaymentTransactionHistory(SuperAdminRequiredMixin, SponsorPaymentNotificationMixin, MessageContextMixin, ListView):
    model = Payment
    template_name = "transaction_history.html"
    context_object_name = "payments"
    login_url = "/login-page"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transaction_history"] = Payment.objects.filter(
            sponsor=self.request.user
        ).order_by('-payment_date')
        return context

class OverduePayments(SuperAdminRequiredMixin, SponsorPaymentNotificationMixin, MessageContextMixin, TemplateView):
    template_name = "overdue.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["monthly_amount"] = MonthlyAmount.objects.first().amount

        return context

class ReceivedMessages(SuperAdminRequiredMixin, SponsorPaymentNotificationMixin, MessageContextMixin, TemplateView):
    template_name = "received_messages.html"
    login_url = "/login-page"
    redirect_field_name = "authentication_required"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages_list"] = Message.objects.filter(
            receiver=self.request.user
        ).order_by("-timestamp")
        return context

class ViewMessage(SuperAdminRequiredMixin, SponsorPaymentNotificationMixin, MessageContextMixin, TemplateView):
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

class UserUpdateView(SuperAdminRequiredMixin, SponsorPaymentNotificationMixin, MessageContextMixin, UpdateView):
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

class PasswordUpdateView(SuperAdminRequiredMixin, SponsorPaymentNotificationMixin, MessageContextMixin, PasswordChangeView):
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
            monthly_amount = MonthlyAmount.objects.first().amount
            amount_in_cents = int(monthly_amount * 100)
            selected_family = get_object_or_404(FamilyList, pk=family_id)

            stripe_session = stripe.checkout.Session.create(
                payment_method_types=[
                    "card",
                ],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": amount_in_cents,
                            "product_data": {
                                "name": selected_family.family_name,
                                 "description": selected_family.family_bio,
                                "images": [
                                    "https://coderspdf.com/wp-content/uploads/2024/12/Screenshot_58.png",
                                    "https://coderspdf.com/wp-content/uploads/2024/12/Screenshot_57.png",
                                    "https://coderspdf.com/wp-content/uploads/2024/12/Screenshot_56.png"
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
                    "amount_paid": monthly_amount,
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
            print("Checkout Session Completed!")
            self.manage_checkout_session(stripe_session)

        return JsonResponse({"status": "success"})

    def manage_checkout_session(self, stripe_session):
        family_id = stripe_session["metadata"]["family_id"]
        sponsor_id = stripe_session["metadata"]["sponsor_id"]

        try:
            user = User.objects.get(id=sponsor_id)
        except User.DoesNotExist:
            print(f"User with ID {sponsor_id} not found.")
            return

        Family_Sponsored = get_object_or_404(FamilyList, pk=family_id)
        try:
            if Payment.objects.exists():
                overdue_payment = Payment.objects.first().overdue_payment + timezone.timedelta(days=30)
            else:
                overdue_payment = timezone.now()
            save_payment = Payment.objects.create(
                sponsor=user,
                family=Family_Sponsored,
                amount=stripe_session["metadata"]["amount_paid"],
                overdue_payment = overdue_payment
            )
            
            exists = SponsorFamilyRelation.objects.filter(sponsor=user, family=Family_Sponsored).exists()
            if not exists:
                SponsorFamilyRelation.objects.create(
                    sponsor=user, 
                    family=Family_Sponsored
                    )
                
            if Family_Sponsored.is_sponsored is False:
                Family_Sponsored.is_sponsored = True
                Family_Sponsored.save()
                
            print(f"Payment successfully created for user {user.id} and family {family_id}")
        except Exception as e:
            print(f"Error saving payment: {str(e)}")
            
class PayPalCheckoutView(SuperAdminRequiredMixin, View):
    
    def get(self, request, family_id, *args, **kwargs):
        try:
            monthly_amount = MonthlyAmount.objects.first().amount
            selected_family = get_object_or_404(FamilyList, pk=family_id)

            paypal_dict = {
                "business": settings.PAYPAL_RECEIVER_EMAIL,
                "amount": str(monthly_amount),
                "item_name": f"Sponsorship payment for {selected_family.family_name}",
                "invoice": str(uuid.uuid4()),
                "currency_code": "USD",
                "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
                "return": request.build_absolute_uri(reverse("payment-success")),
                "cancel_return": request.build_absolute_uri(reverse("payment-cancel")),
                "custom": f"{selected_family.id}|{request.user.id}",
            }

            form = PayPalPaymentsForm(initial=paypal_dict)
            return render(request, 'process_payment.html', {'form': form})


        except Exception as e:
            logger.error(f"Error during PayPal checkout: {str(e)}")
            messages.error(request, "An error occurred during checkout.")
            return redirect("family-list-page")

class PaymentSuccessView(SuperAdminRequiredMixin, SponsorPaymentNotificationMixin, MessageContextMixin, TemplateView):
    login_url = "/login-page"
    template_name = "payment_success.html"

class PaymentCancelView(SuperAdminRequiredMixin, SponsorPaymentNotificationMixin, MessageContextMixin, TemplateView):
    login_url = "/login-page"
    template_name = "payment_cancel.html"