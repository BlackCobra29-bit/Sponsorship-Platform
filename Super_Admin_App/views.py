from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .mixins import TransactionContextMixin, SponsorPaymentNotificationMixin
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import Payment, Administrator
from django.utils.crypto import get_random_string
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, TemplateView, CreateView, ListView, UpdateView, DeleteView, DetailView
from .models import FamilyList, FamilyImage, MonthlyAmount
from Sponsor_App.models import SponosrAccount, SponsorFamilyRelation
from .forms import FamilyListForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import PasswordChangeView
from .forms import UserModelForm, CustomPasswordChangeForm
from django.shortcuts import redirect
from django.contrib.auth.models import User

# Helper to restrict view access to superadmins
from django.contrib.auth.mixins import LoginRequiredMixin

class SuperAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect("admin-login")
        return super().dispatch(request, *args, **kwargs)

# Dashboard View (CBV)
class DashboardView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Remove users who are not superadmins and are not sponsors in any SponsorFamilyRelation
        active_sponsor_ids = SponsorFamilyRelation.objects.values_list('sponsor', flat=True)
        inactive_sponsors = User.objects.exclude(id__in=active_sponsor_ids).filter(is_superuser=False)
        count_deleted, _ = inactive_sponsors.delete()

        # Retrieve statistics
        context["total_families"] = FamilyList.objects.count()
        context["sponsored_families"] = FamilyList.objects.filter(is_sponsored=True).count()
        context["unsponsored_families"] = FamilyList.objects.filter(is_sponsored=False).count()
        context["unique_sponsors"] = User.objects.filter(sponsored_families__isnull=False).distinct().count()
        context["total_amount_paid"] = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        context["male_families"] = FamilyList.objects.filter(gender = "Male").count()
        context["female_families"] = FamilyList.objects.filter(gender = "Female").count()
        context["unknown_families"] = FamilyList.objects.filter(gender = "Unknown").count()

        return context

# Sponsored management Page View (CBV)
class SponsorManagementPage(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, TemplateView):
    template_name = 'sponsors_management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sponsors = SponosrAccount.objects.all()
        
        # Adding the total amount paid by each sponsor
        sponsors_with_payments = []
        for sponsor_account in sponsors:
            total_paid = Payment.objects.filter(sponsor=sponsor_account.user).aggregate(total=Sum('amount'))['total'] or 0
            sponsors_with_payments.append({
                'sponsor_account': sponsor_account,
                'total_paid': total_paid
            })
        
        context["sponsors_with_payments"] = sponsors_with_payments
        return context


# Add Family View (CBV)
class AddFamilyView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, CreateView):
    template_name = "add_family.html"
    model = FamilyList
    fields = ['family_name', 'location', 'contact_address', 'family_bio']

    def post(self, request, *args, **kwargs):
        family = FamilyList.objects.create(
            family_name=request.POST.get('family_name'),
            gender=request.POST.get('gender'),
            location=request.POST.get('location'),
            contact_address=request.POST.get('contact_address'),
            bank_account = request.POST.get('bank_account'),
            family_bio=request.POST.get('family_bio'),
        )

        images = request.FILES.getlist('images')

        if not images:
                FamilyImage.objects.create(family=family, photo='avatars/allgender.png')
        else:
            for image in images:
                FamilyImage.objects.create(family=family, photo=image)


        return JsonResponse({"success": True, "message": "Family added successfully!"})


# Family Management View (CBV)
class FamilyManagementView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, ListView):
    template_name = "family_management.html"
    model = FamilyList
    context_object_name = 'total_families'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve all families
        families = FamilyList.objects.all()

        # Prepare a list of families with their associated payments (active and inactive)
        families_with_payments = []
        for family in families:
            payments = Payment.objects.filter(family=family)

            # Filter payments based on their active status
            unpaid_payments = payments.filter(is_active=True)
            paid_payments = payments.filter(is_active=False)

            # Calculate total amounts for both unpaid and paid payments
            total_unpaid_amount = unpaid_payments.aggregate(total=Sum('amount'))['total'] or 0
            total_paid_amount = paid_payments.aggregate(total=Sum('amount'))['total'] or 0

            families_with_payments.append({
                'family': family,
                'unpaid_payments': unpaid_payments,
                'paid_payments': paid_payments,
                'total_unpaid_amount': total_unpaid_amount,
                'total_paid_amount': total_paid_amount
            })

        context['families_with_payments'] = families_with_payments
        
        return context
    
class UnpaidPaymentsView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, TemplateView):
    template_name = 'unpaid_payments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family_id = self.kwargs['family_id']
        
        # Retrieve the family by ID
        family = get_object_or_404(FamilyList, pk=family_id)
        unpaid_payments = Payment.objects.filter(family=family, is_active=True)

        context['family'] = family
        context['unpaid_payments'] = unpaid_payments
        return context
    
class MarkPaymentsPaidView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, View):
    def post(self, request, family_id):
        # Retrieve the family based on the given family_id
        family = get_object_or_404(FamilyList, id=family_id)
        
        # Get the selected payment IDs from the form
        payment_ids = request.POST.getlist('payment_ids')
        
        # Update the payments to set them as inactive (paid)
        Payment.objects.filter(id__in=payment_ids, family=family).update(is_active=False)
        
        # Redirect back to the unpaid payments page for this family
        return redirect('unpaid-payments', family_id=family_id)

# Family Update View (CBV)
class FamilyListUpdateView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, UpdateView):
    model = FamilyList
    form_class = FamilyListForm
    template_name = "family_update.html"
    success_url = reverse_lazy("family-management")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["family"] = self.object
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Family details updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the family details.')
        return super().form_invalid(form)
    
# Delete Family Image View (CBV)
class FamilyListDeleteView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, TemplateView):
    model = FamilyList
    success_url = reverse_lazy("family-management")

    def post(self, request, *args, **kwargs):
        family = get_object_or_404(FamilyList, pk=kwargs['pk'])
        
        # Check if there are any unpaid payments
        total_unpaid_amount = Payment.objects.filter(family=family, is_active=True).aggregate(total=Sum('amount'))['total'] or 0
        
        if total_unpaid_amount == 0:
            family.delete()
            messages.success(request, "Family removed successfully.")
        else:
            messages.error(request, "Family cannot be deleted because there are unpaid payments.")

        return redirect(self.success_url)

# Update Family Image View (CBV)
class UpdateFamilyImageView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, TemplateView):

    def post(self, request, image_id):
        image = get_object_or_404(FamilyImage, id=image_id)
        new_image = request.FILES.get('new_image')
        if new_image:
            image.photo.delete()
            image.photo = new_image
            image.save()
        return redirect('family-update', pk=image.family.id)


# Delete Family Image View (CBV)
class DeleteFamilyImageView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, TemplateView):

    def post(self, request, image_id):
        image = get_object_or_404(FamilyImage, id=image_id)
        family_id = image.family.id
        image.photo.delete()
        image.delete()
        messages.success(request, "The family image was successfully deleted.")
        return redirect('family-update', pk=family_id)


# Family Delete View (CBV)
class FamilyUnsponsorView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, View):
    model = FamilyList
    success_url = reverse_lazy("family-management")

    def post(self, request, *args, **kwargs):
        family = get_object_or_404(FamilyList, pk=kwargs['pk'])
        
        # Unsponsoring the family
        family.is_sponsored = False
        family.save()
        
        # Remove the SponsorFamilyRelation
        SponsorFamilyRelation.objects.filter(family=family).delete()  # Delete all relations for the family

        messages.success(request, "Family removed successfully.")
        return redirect(self.success_url)

# Export Family Data View (CBV)
class ExportFamilyDataView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, TemplateView):
    template_name = "export-family-data.html"

    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve all families
        families = FamilyList.objects.all()

        # Prepare a list of families with their associated payments (active and inactive)
        families_with_payments = []
        for family in families:
            payments = Payment.objects.filter(family=family)

            # Filter payments based on their active status
            unpaid_payments = payments.filter(is_active=True)
            paid_payments = payments.filter(is_active=False)

            # Calculate total amounts for both unpaid and paid payments
            total_unpaid_amount = unpaid_payments.aggregate(total=Sum('amount'))['total'] or 0
            total_paid_amount = paid_payments.aggregate(total=Sum('amount'))['total'] or 0

            families_with_payments.append({
                'family': family,
                'unpaid_payments': unpaid_payments,
                'paid_payments': paid_payments,
                'total_unpaid_amount': total_unpaid_amount,
                'total_paid_amount': total_paid_amount
            })

        context['families_with_payments'] = families_with_payments
        
        return context
    

# Monthly sponsorship amount View (CBV)
class MonthlySponsorshipAmount(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, TemplateView):
    template_name = "settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        monthly_amount = get_object_or_404(MonthlyAmount)
        context['amount'] = monthly_amount.amount
        return context

    def post(self, request, *args, **kwargs):
        monthly_amount = get_object_or_404(MonthlyAmount)
        new_amount = request.POST.get('monthly_amount')
        if new_amount:
            monthly_amount.amount = new_amount
            monthly_amount.save()

        return JsonResponse({"success": True, "message": "Monthly amount updated successfully!"})

class UserAdminUpdateView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, UpdateView):
    model = User
    form_class = UserModelForm
    template_name = "admin_account_update.html"
    success_url = reverse_lazy("admin-dashboard")

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
    
class PasswordAdminUpdateView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'admin_password_change.html'
    success_url = reverse_lazy('admin-dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Password updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the Password.')
        return super().form_invalid(form)
    
class CreateAdminAccount(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, TemplateView):
    template_name = 'create_super_admin.html'

    def post(self, request):
        # Retrieve values from the POST data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('admin_email')
        admin_photo = request.FILES.get('admin_photo')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": "Email already taken. Please use another.",
                }
            )
            
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": "Username already taken. Please use another.",
                }
            )

        # Generate a 6-digit random password
        password = get_random_string(length=6, allowed_chars='0123456789')

        print(f"Password is: {password}")

        try:
            # Create the superuser
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,
                is_superuser=True
            )
            user.set_password(password)
            user.save()

            # Create an Administrator instance and save the admin photo
            Administrator.objects.create(
                user=user,
                admin_photo=admin_photo
            )

            # Prepare the email content
            subject = 'New Admin Account Created'
            message = render_to_string('email_template.html', {
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'password': password,
            })

            # Send the email
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],  # Send to the new admin's email
                fail_silently=False,
                html_message=message  # This allows for HTML content
            )

            # Return a success response with a message
            return JsonResponse(
                {
                    "success": True,
                    "message": "The admin account has been successfully created, and the login details have been sent to the provided email address.",
                }
            )

        except Exception as e:
            # Print the error to the console for debugging
            print(f"An error occurred: {str(e)}")  # This will display the error in the console
            
            return JsonResponse(
                {
                    "success": False,
                    "message": f"An error occurred: {str(e)}"
                }
            )   

class PaymentHistoryView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, ListView):
    model = Payment
    template_name = 'payment_history.html'
    context_object_name = 'payments'

    def get_queryset(self):
        # Get all payments
        payments = Payment.objects.all()

        return payments
    
class PaymentDetailView(SuperAdminRequiredMixin, TransactionContextMixin, SponsorPaymentNotificationMixin, DetailView):
    model = Payment
    template_name = 'payment_detail.html'
    context_object_name = 'payment'

    def get_object(self):
        pk = self.kwargs.get('pk')
        payment = get_object_or_404(Payment, pk=pk)

        # Update the is_seen attribute and save
        if not payment.is_seen:
            payment.is_seen = True
            payment.save()
        
        return payment

# End of the view page