from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import FamilyList
from .models import FamilyImage
from .forms import FamilyListForm
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages


# Create your views here.
@login_required(login_url="/login-page", redirect_field_name="authentication_required")
def dashboard(request):

    total_family_count = FamilyList.objects.all().count()
    unsponsored_family_count = FamilyList.objects.filter(is_sponsored=False).count()

    context = {
        "total_family_count": total_family_count,
        "unsponsored_family_count": unsponsored_family_count,
    }

    return render(request, "dashboard.html", context)


@login_required(login_url="/login-page", redirect_field_name="authentication_required")
def AddFamily(request):
    if request.method == "POST":
        family_name = request.POST["family_name"]
        location = request.POST["location"]
        contact_address = request.POST["contact_address"]
        no_of_family_members = request.POST["no_of_family_members"]
        family_bio = request.POST["family_bio"]

        # Create the SponsoredFamily instance
        family = FamilyList.objects.create(
            family_name=family_name,
            location=location,
            contact_address=contact_address,
            no_of_family_members=no_of_family_members,
            family_bio=family_bio,
        )

        # Handle multiple image uploads
        images = request.FILES.getlist("images")
        for image in images:
            FamilyImage.objects.create(family=family, photo=image)

        # Return success response
        return JsonResponse({"success": True, "message": "Family added successfully!"})

    return render(request, "add_family.html")


@login_required(login_url="/login-page", redirect_field_name="authentication_required")
def FamilyManagement(request):

    total_families = FamilyList.objects.all()

    context = {"total_families": total_families}

    return render(request, "family_management.html", context)


@method_decorator(
    login_required(
        login_url="/login-page", redirect_field_name="authentication_required"
    ),
    name="dispatch",
)
class FamilyListUpdateView(UpdateView):
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

@login_required(login_url="/login-page", redirect_field_name="authentication_required")
def UpdateFamilyImage(request, image_id):
    image = get_object_or_404(FamilyImage, id=image_id)
    if request.method == 'POST':
        new_image = request.FILES.get('new_image')
        if new_image:
            image.photo.delete()
            image.photo = new_image
            image.save()
        return redirect('family-update', pk=image.family.id)
    return redirect('family-update', pk=image.family.id)

@login_required(login_url="/login-page", redirect_field_name="authentication_required")
def DeleteFamilyImage(request, image_id):
    image = get_object_or_404(FamilyImage, id=image_id)
    family_id = image.family.id
    if request.method == 'POST':
        image.photo.delete()
        image.delete()
        return redirect('family-update', pk=family_id)
    return redirect('family-update', pk=family_id)

@method_decorator(
    login_required(
        login_url="/login-page", redirect_field_name="authentication_required"
    ),
    name="dispatch",
)
class FamilyDeleteView(DeleteView):
    model = FamilyList
    success_url = reverse_lazy("family-management")

@login_required(login_url="/login-page", redirect_field_name="authentication_required")
def ExportFamilyData(request):
    
    total_families = FamilyList.objects.all()

    context = {"total_families": total_families}

    return render(request, "export-family-data.html", context)