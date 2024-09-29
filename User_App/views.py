from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from Super_Admin_App.models import FamilyList
from django.core.paginator import Paginator


class HomeView(ListView):
    model = FamilyList
    template_name = "home.html"
    context_object_name = "unsponsored_families"
    paginate_by = 30

    def get_queryset(self):
        return FamilyList.objects.filter(is_sponsored=False).prefetch_related("images")[:30]


class FamiliesListPage(ListView):
    model = FamilyList
    template_name = "families_page.html"
    context_object_name = "page_obj"
    paginate_by = 6

    def get_queryset(self):
        return FamilyList.objects.filter(is_sponsored=False).prefetch_related("images")


class AboutUsPage(TemplateView):
    template_name = "about_us.html"