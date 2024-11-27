from django.contrib import admin
from django.urls import path, include
from .views import home_page_view, secret_view, users_only_view, staff_only_view
from user_auth import views as auth_views


urlpatterns = [
    path("", home_page_view, name="home"),
    path("accounts/", include("allauth.urls")),
    path("profiles/", include("profiles.urls")),
    path("login/", auth_views.login_view, name="login"),
    path("signup/", auth_views.signup_view, name="signup"),
    path("admin/", admin.site.urls),
    path("protected/", secret_view),
    path("protected/user-only/", users_only_view),
    path("protected/staff-only/", staff_only_view),
]
