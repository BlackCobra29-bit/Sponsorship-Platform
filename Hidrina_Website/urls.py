from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# import User_App view urls
from User_App.views import home_view
from User_App.views import FamiliesListPage
from User_App.views import AboutUsPage
# import Auth_App urls
from Auth_App.views import render_login_page
from Auth_App.views import render_logout
from Auth_App.views import render_forgot_password_page
from Auth_App.views import render_create_account_page
# import Sponsor_App urls
from Sponsor_App.views import home_page
from Sponsor_App.views import my_sponsorship
# import Super_Admin_App urls
from Super_Admin_App.views import dashboard
from Super_Admin_App.views import AddFamily
from Super_Admin_App.views import FamilyManagement

urlpatterns = [
    path('admin/', admin.site.urls),
    # url pattern for User_App
    path('', home_view, name='home-page'),
    path('families-list/', FamiliesListPage, name='family-list-page'),
    path('about-us/', AboutUsPage, name='about-us-page'),
    # url pattern for Auth_App
    path('login-page/', render_login_page, name = 'admin-login'),
    path('logout-page/', render_logout, name = 'admin-logout'),
    path('forgot-password/', render_forgot_password_page, name = 'forgot-password'),
    path('create-account/', render_create_account_page, name = 'create-account'),
    # url pattern for Sponsor_App
    path('home/', home_page, name = 'sponsor-home-page'),
    path('my-sponsorship/', my_sponsorship, name = 'my-sponsorship'),
    # url pattern for Super_Admin_Base
    path('dashboard/', dashboard, name = 'admin-dashboard'),
    path('add-family/', AddFamily, name = 'add-family'),
    path('family-management/', FamilyManagement, name = 'family-management'),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)