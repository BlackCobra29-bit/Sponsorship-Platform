from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import FamilyList
from .models import FamilyImage


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

    context = {
        'total_families': total_families
    }

    return render(request, 'family_management.html', context)