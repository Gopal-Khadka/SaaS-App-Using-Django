from django.contrib import admin
from django.urls import path, include
from .views import home_page_view, secret_view, users_only_view, staff_only_view
from user_auth import views as auth_views
from subscriptions import views as subs_views
from checkouts import views as checkout_views
from landing import views as landing_views

urlpatterns = [
    path("", landing_views.landing_page_view, name="home"),
    path("profiles/", include("profiles.urls")),
    path("admin/", admin.site.urls),
    path(
        "accounts/billing", subs_views.user_subscription_view, name="user_subscription"
    ),
    path(
        "accounts/billing/cancel", subs_views.user_subscription_cancel_view, name="user_subscription_cancel"
    ),
    path("accounts/", include("allauth.urls")),
    path("pricing/<str:interval>", subs_views.subscription_price_view, name="pricing"),
    path(
        "checkout/sub-price/<int:price_id>",
        checkout_views.product_price_redirect_view,
        name="sub-price-checkout",
    ),
    path(
        "checkout/start/",
        checkout_views.checkout_redirect_view,
        name="stripe-checkout-start",
    ),
    path(
        "checkout/success/",
        checkout_views.checkout_finalized_view,
        name="stripe-checkout-end",
    ),
    # path("protected/", secret_view),
    # path("protected/user-only/", users_only_view),
    # path("protected/staff-only/", staff_only_view),
]
