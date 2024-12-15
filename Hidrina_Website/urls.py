from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# import User_App view urls
from User_App.views import HomeView, FamiliesListPage, FamilyDetailView, AboutUsPage

# import Auth_App urls
from Auth_App.views import LoginView, LogoutView, ForgotPasswordView, DeleteAccountView

# import Sponsor_App views
from Sponsor_App.views import (
    SponsorHomePage,
    MySponsorshipPage,
    ReceivedMessages,
    ViewMessage,
    UserUpdateView,
    PasswordUpdateView,
    PaymentSuccessView,
    PaymentCancelView,
    StripeCheckoutView,
    WebhookManagerView,
    PaymentTransactionHistory,
    PayPalCheckoutView,
    OverduePayments,
)

# import Super_Admin_App urls
from Super_Admin_App.views import (
    DashboardView,
    AddFamilyView,
    FamilyManagementView,
    FamilyListUpdateView,
    FamilyUnsponsorView,
    UpdateFamilyImageView,
    DeleteFamilyImageView,
    ExportFamilyDataView,
    MonthlySponsorshipAmount,
    SponsorManagementPage,
    PasswordAdminUpdateView,
    UserAdminUpdateView,
    UnpaidPaymentsView,
    MarkPaymentsPaidView,
    CreateAdminAccount,
    PaymentHistoryView,
    PaymentDetailView
)

# import Messaging views
from Messaging.views import MailPageView, ComposePageView, ViewMessageAdmin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("captcha/", include("captcha.urls")),

    # url pattern for User_App
    path("", HomeView.as_view(), name="home-page"),
    path("family-detail/", FamilyDetailView.as_view(), name = "family-detail"),
    path(
        "families-list/", FamiliesListPage.as_view(), name="family-list-page"
    ),
    path("about-us/", AboutUsPage.as_view(), name="about-us-page"),

    # url pattern for Auth_App
    path("login-page/", LoginView.as_view(), name="admin-login"),
    path("logout-page/", LogoutView.as_view(), name="admin-logout"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path('delete-account/<int:pk>/', DeleteAccountView.as_view(), name='delete-account'),

    # url pattern for Sponsor_App
    path("home/", SponsorHomePage.as_view(), name="sponsor-home-page"),
    path("my-sponsorship/", MySponsorshipPage.as_view(), name="my-sponsorship"),
    path("received-messages/", ReceivedMessages.as_view(), name="received-messages"),
    path("view-message/", ViewMessage.as_view(), name="view-message"),
    path("account/<int:pk>/update/", UserUpdateView.as_view(), name="update-account"),
    path("password/change/", PasswordUpdateView.as_view(), name="password_change"),
    path("stripe-checkout/<int:family_id>", StripeCheckoutView.as_view(), name="stripe-checkout"),
    path("stripe-checkout-webhook", WebhookManagerView.as_view(), name = "stripe-webhook-manager"),
    path("paypal-checkout/<int:family_id>", PayPalCheckoutView.as_view(), name="paypal-checkout"),
    path("payment-success/", PaymentSuccessView.as_view(), name = "payment-success"),
    path("payment-cancel/", PaymentCancelView.as_view(), name = "payment-cancel"),
    path("transaction-history/", PaymentTransactionHistory.as_view(), name = "transaction-history"),
    path("overdue-payments/", OverduePayments.as_view(), name = "overdue-payments"),

    # url pattern for Super_Admin_Base
    path("dashboard/", DashboardView.as_view(), name="admin-dashboard"),
    path(
        "family-sponsors/", SponsorManagementPage.as_view(), name="sponsors-management"
    ),
    path("add-family/", AddFamilyView.as_view(), name="add-family"),
    path(
        "family-management/", FamilyManagementView.as_view(), name="family-management"
    ),
    path('unpaid-payments/<int:family_id>/', UnpaidPaymentsView.as_view(), name='unpaid-payments'),
    path('mark-payments-paid/<int:family_id>/', MarkPaymentsPaidView.as_view(), name='mark-payments-paid'),
    path(
        "family/<int:pk>/update/", FamilyListUpdateView.as_view(), name="family-update"
    ),
    path("family/<int:pk>/delete/", FamilyUnsponsorView.as_view(), name="family-unsponsor"),
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
    path(
        "sponsor-settings/",
        MonthlySponsorshipAmount.as_view(),
        name="monthly-sponsorship-settings",
    ),
    path("admin-account/<int:pk>/update/", UserAdminUpdateView.as_view(), name="admin-account-update"),
    path("admin-password/change/", PasswordAdminUpdateView.as_view(), name="password_admin_change"),
    path("create-admin-account/", CreateAdminAccount.as_view(), name = "admin-account"),
    path("payment-history/", PaymentHistoryView.as_view(), name = "payment-history"),
    path('payment/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),

    # url pattern for Messaging App
    path("mail-page/", MailPageView.as_view(), name="mail-page"),
    path("send-message/", ComposePageView.as_view(), name="compose-page"),
    path("view-message-admin/", ViewMessageAdmin.as_view(), name="view-message-admin"),

    # url pattern for password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # Add this new PayPal URL pattern
    path('paypal/', include('paypal.standard.ipn.urls')),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)