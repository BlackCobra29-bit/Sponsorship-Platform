from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from .models import FamilyList, FamilyImage
from .forms import FamilyListForm
from django.urls import reverse_lazy
from django.contrib import messages


# Dashboard View (CBV)
class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = "/login-page"
    redirect_field_name = "authentication_required"
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_family_count'] = FamilyList.objects.all().count()
        context['unsponsored_family_count'] = FamilyList.objects.filter(is_sponsored=False).count()
        return context


# Add Family View (CBV)
class AddFamilyView(LoginRequiredMixin, CreateView):
    login_url = "/login-page"
    redirect_field_name = "authentication_required"
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
class FamilyManagementView(LoginRequiredMixin, ListView):
    login_url = "/login-page"
    redirect_field_name = "authentication_required"
    template_name = "family_management.html"
    model = FamilyList
    context_object_name = 'total_families'


# Family Update View (already CBV)
class FamilyListUpdateView(LoginRequiredMixin, UpdateView):
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
        messages.error(self.request, 'There was an error updating the family details. Please correct the errors below.')
        return super().form_invalid(form)


# Update Family Image View (CBV)
class UpdateFamilyImageView(LoginRequiredMixin, TemplateView):
    login_url = "/login-page"
    redirect_field_name = "authentication_required"

    def post(self, request, image_id):
        image = get_object_or_404(FamilyImage, id=image_id)
        new_image = request.FILES.get('new_image')
        if new_image:
            image.photo.delete()
            image.photo = new_image
            image.save()
        return redirect('family-update', pk=image.family.id)


# Delete Family Image View (CBV)
class DeleteFamilyImageView(LoginRequiredMixin, TemplateView):
    login_url = "/login-page"
    redirect_field_name = "authentication_required"

    def post(self, request, image_id):
        image = get_object_or_404(FamilyImage, id=image_id)
        family_id = image.family.id
        image.photo.delete()
        image.delete()
        return redirect('family-update', pk=family_id)


# Family Delete View (already CBV)
class FamilyDeleteView(LoginRequiredMixin, DeleteView):
    model = FamilyList
    success_url = reverse_lazy("family-management")


# Export Family Data View (CBV)
class ExportFamilyDataView(LoginRequiredMixin, TemplateView):
    login_url = "/login-page"
    redirect_field_name = "authentication_required"
    template_name = "export-family-data.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_families'] = FamilyList.objects.all()
        return context