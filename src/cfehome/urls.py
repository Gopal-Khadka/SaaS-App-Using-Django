from django.contrib import admin
from django.urls import path, include
from .views import home_page_view, secret_view, users_only_view, staff_only_view
from user_auth import views as auth_views
from subscriptions import views as subs_views

urlpatterns = [
    path("", home_page_view, name="home"),
    path("accounts/", include("allauth.urls")),
    path("profiles/", include("profiles.urls")),
    path("admin/", admin.site.urls),
    path("pricing/<str:interval>", subs_views.subscription_price_view, name="pricing"),
    # path("protected/", secret_view),
    # path("protected/user-only/", users_only_view),
    # path("protected/staff-only/", staff_only_view),
]
