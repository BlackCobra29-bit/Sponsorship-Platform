from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.views.generic import ListView, TemplateView, DetailView
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from Super_Admin_App.models import FamilyList
from Sponsor_App.models import SponosrAccount
from django_countries import countries

class HomeView(ListView):
    model = FamilyList
    template_name = "home.html"
    context_object_name = "unsponsored_families"
    paginate_by = 30

    def get_queryset(self):
        return FamilyList.objects.filter(is_sponsored=False).prefetch_related("images")[
            :30
        ]


class FamilyDetailView(DetailView):
    model = FamilyList
    template_name = "family_detail.html"
    context_object_name = "family"

    def get_object(self):
        family_id = self.request.GET.get("family-id")
        return get_object_or_404(FamilyList, id=family_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = countries  # Ensure you have this list available
        return context

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        location = request.POST.get("country_location")
        phone = request.POST.get("phone_number")
        sponsor_photo = request.FILES.get("photo")

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": "Username already taken. Please choose another.",
                }
            )
            
        if User.objects.filter(email = email).exists():
            return JsonResponse({
                "success": False,
                "message": "Email already taken. Please use another."
            })

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=make_password(password),
        )

        SponosrAccount.objects.create(
            user=user,
            phone_number=phone,
            location=location,
            sponsor_photo=sponsor_photo
        )

        # Log the user in
        login(request, user)

        return JsonResponse(
            {
                "success": True,
                "message": "Account created successfully.",
            }
        )


class FamiliesListPage(ListView):
    model = FamilyList
    template_name = "families_page.html"
    context_object_name = "page_obj"
    paginate_by = 6

    def get_queryset(self):
        return FamilyList.objects.filter(is_sponsored=False).prefetch_related("images")


class AboutUsPage(TemplateView):
    template_name = "about_us.html"