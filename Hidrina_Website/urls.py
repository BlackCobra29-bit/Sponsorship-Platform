from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# import User_App view urls
from User_App.views import home_view
from User_App.views import FamiliesListPage
from User_App.views import AboutUsPage
# import Auth_App urls
from Auth_App.views import (LoginView, 
                            LogoutView, 
                            ForgotPasswordView, 
                            CreateAccountView)
# import Sponsor_App urls
from Sponsor_App.views import home_page
from Sponsor_App.views import my_sponsorship
# import Super_Admin_App urls
from Super_Admin_App.views import dashboard
from Super_Admin_App.views import AddFamily
from Super_Admin_App.views import FamilyManagement
from Super_Admin_App.views import FamilyListUpdateView
from Super_Admin_App.views import FamilyDeleteView
from Super_Admin_App.views import UpdateFamilyImage
from Super_Admin_App.views import DeleteFamilyImage
from Super_Admin_App.views import ExportFamilyData
# import Messaging urls
from Messaging.views import MailPage, ComposePage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    # url pattern for User_App
    path('', home_view, name='home-page'),
    path('families-list/', FamiliesListPage, name='family-list-page'),
    path('about-us/', AboutUsPage, name='about-us-page'),
    # url pattern for Auth_App
    path('login-page/', LoginView.as_view(), name='admin-login'),
    path('logout-page/', LogoutView.as_view(), name='admin-logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('create-account/', CreateAccountView.as_view(), name='create-account'),
    # url pattern for Sponsor_App
    path('home/', home_page, name='sponsor-home-page'),
    path('my-sponsorship/', my_sponsorship, name='my-sponsorship'),
    # url pattern for Super_Admin_Base
    path('dashboard/', dashboard, name='admin-dashboard'),
    path('add-family/', AddFamily, name='add-family'),
    path('family-management/', FamilyManagement, name='family-management'),
    path('family/<int:pk>/update/', FamilyListUpdateView.as_view(), name='family-update'),
    path('family/<int:pk>/delete/', FamilyDeleteView.as_view(), name='family-delete'),
    path('family/image/<int:image_id>/update/', UpdateFamilyImage, name='update_family_image'),
    path('family/image/<int:image_id>/delete/', DeleteFamilyImage, name='delete_family_image'),
    path('export-data/', ExportFamilyData, name='export-family-data'),
    # url pattern for Super_Admin_Base
    path('mail-page', MailPage, name = "mail-page"),
    path('compose-page', ComposePage, name = "compose-page"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)