from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Payment
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from .models import FamilyList, FamilyImage, MonthlyAmount
from Sponsor_App.models import SponosrAccount
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
class DashboardView(SuperAdminRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the total number of families
        context["total_families"] = FamilyList.objects.count()
        
        # Retrieve the number of sponsored families
        context["sponsored_families"] = FamilyList.objects.filter(is_sponsored=True).count()
        
        # Retrieve the number of unique sponsors
        context["unique_sponsors"] = User.objects.filter(sponsored_families__isnull=False).distinct().count()
        
        # Retrieve the total amount paid by all users
        context["total_amount_paid"] = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

        return context

# Sponsored management Page View (CBV)
class SponsorManagementPage(SuperAdminRequiredMixin, TemplateView):
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
class AddFamilyView(SuperAdminRequiredMixin, CreateView):
    template_name = "add_family.html"
    model = FamilyList
    fields = ['family_name', 'location', 'contact_address', 'no_of_family_members', 'family_bio']

    def post(self, request, *args, **kwargs):
        family = FamilyList.objects.create(
            family_name=request.POST.get('family_name'),
            location=request.POST.get('location'),
            contact_address=request.POST.get('contact_address'),
            no_of_family_members=request.POST.get('no_of_family_members'),
            family_bio=request.POST.get('family_bio'),
        )

        images = request.FILES.getlist('images')
        for image in images:
            FamilyImage.objects.create(family=family, photo=image)

        return JsonResponse({"success": True, "message": "Family added successfully!"})


# Family Management View (CBV)
class FamilyManagementView(SuperAdminRequiredMixin, ListView):
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

# Family Update View (CBV)
class FamilyListUpdateView(SuperAdminRequiredMixin, UpdateView):
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


# Update Family Image View (CBV)
class UpdateFamilyImageView(SuperAdminRequiredMixin, TemplateView):

    def post(self, request, image_id):
        image = get_object_or_404(FamilyImage, id=image_id)
        new_image = request.FILES.get('new_image')
        if new_image:
            image.photo.delete()
            image.photo = new_image
            image.save()
        return redirect('family-update', pk=image.family.id)


# Delete Family Image View (CBV)
class DeleteFamilyImageView(SuperAdminRequiredMixin, TemplateView):

    def post(self, request, image_id):
        image = get_object_or_404(FamilyImage, id=image_id)
        family_id = image.family.id
        image.photo.delete()
        image.delete()
        return redirect('family-update', pk=family_id)


# Family Delete View (CBV)
class FamilyDeleteView(SuperAdminRequiredMixin, DeleteView):
    model = FamilyList
    success_url = reverse_lazy("family-management")


# Export Family Data View (CBV)
class ExportFamilyDataView(SuperAdminRequiredMixin, TemplateView):
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
class MonthlySponsorshipAmount(SuperAdminRequiredMixin, TemplateView):
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

class UserAdminUpdateView(SuperAdminRequiredMixin, UpdateView):
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
    
class PasswordAdminUpdateView(SuperAdminRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'admin_password_change.html'
    success_url = reverse_lazy('admin-dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Password updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the Password.')
        return super().form_invalid(form)