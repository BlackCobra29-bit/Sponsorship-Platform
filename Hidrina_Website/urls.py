from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# import User_App view urls
from User_App.views import HomeView, FamiliesListPage, AboutUsPage

# import Auth_App urls
from Auth_App.views import LoginView, LogoutView, ForgotPasswordView, CreateAccountView

# import Sponsor_App views
from Sponsor_App.views import SponsorHomePage, MySponsorshipPage, ReceivedMessages, ViewMessage

# import Super_Admin_App urls
from Super_Admin_App.views import (
    DashboardView,
    AddFamilyView,
    FamilyManagementView,
    FamilyListUpdateView,
    FamilyDeleteView,
    UpdateFamilyImageView,
    DeleteFamilyImageView,
    ExportFamilyDataView,
    MonthlySponsorshipAmount,
    SponsorManagementPage,
)

# import Messaging views
from Messaging.views import MailPageView, ComposePageView, ViewMessageAdmin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("captcha/", include("captcha.urls")),
    # url pattern for User_App
    path("", HomeView.as_view(), name="home-page"),  # Changed to CBV
    path(
        "families-list/", FamiliesListPage.as_view(), name="family-list-page"
    ),  # Changed to CBV
    path("about-us/", AboutUsPage.as_view(), name="about-us-page"),  # Changed to CBV
    # url pattern for Auth_App
    path("login-page/", LoginView.as_view(), name="admin-login"),
    path("logout-page/", LogoutView.as_view(), name="admin-logout"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("create-account/", CreateAccountView.as_view(), name="create-account"),
    # url pattern for Sponsor_App
    path(
        "home/", SponsorHomePage.as_view(), name="sponsor-home-page"
    ), 
    path(
        "my-sponsorship/", MySponsorshipPage.as_view(), name="my-sponsorship"
    ),  
    path(
        "received-messages/", ReceivedMessages.as_view(), name="received-messages"
    ),  
    path(
        "view-message/", ViewMessage.as_view(), name="view-message"
    ), 
    # url pattern for Super_Admin_Base
    path("dashboard/", DashboardView.as_view(), name="admin-dashboard"),
    path("family-sponsors/", SponsorManagementPage.as_view(), name="sponsors-management"),
    path("add-family/", AddFamilyView.as_view(), name="add-family"),
    path(
        "family-management/", FamilyManagementView.as_view(), name="family-management"
    ),
    path(
        "family/<int:pk>/update/", FamilyListUpdateView.as_view(), name="family-update"
    ),
    path("family/<int:pk>/delete/", FamilyDeleteView.as_view(), name="family-delete"),
    path(
        "family/image/<int:image_id>/update/",
        UpdateFamilyImageView.as_view(),
        name="update_family_image",
    ),
    path(
        "family/image/<int:image_id>/delete/",
        DeleteFamilyImageView.as_view(),
        name="delete_family_image",
    ),
    path("export-data/", ExportFamilyDataView.as_view(), name="export-family-data"),
    path("sponsor-settings/", MonthlySponsorshipAmount.as_view(), name = "monthly-sponsorship-settings"),
    # url pattern for Messaging App
    path("mail-page/", MailPageView.as_view(), name="mail-page"),
    path("send-message/", ComposePageView.as_view(), name="compose-page"),
    path("view-message-admin/", ViewMessageAdmin.as_view(), name = "view-message-admin")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
