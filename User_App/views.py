from django.shortcuts import render
from Super_Admin_App.models import FamilyList
from django.core.paginator import Paginator


# Create your views here.
def home_view(request):
    unsponsored_families = FamilyList.objects.filter(
        is_sponsored=False
    ).prefetch_related("images")[:30]

    context = {"unsponsored_families": unsponsored_families}

    return render(request, "home.html", context)


def FamiliesListPage(request):
    unsponsored_families = FamilyList.objects.filter(
        is_sponsored=False
    ).prefetch_related("images")

    # Pagination: 12 families per page (you can adjust this number)
    paginator = Paginator(unsponsored_families, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }

    return render(request, "families_page.html", context)


def AboutUsPage(request):

    return render(request, "about_us.html")
