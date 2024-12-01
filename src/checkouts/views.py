import helpers.billing
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from subscriptions.models import SubscriptionPrice


def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session["checkout_subscription_price_id"] = price_id
    return redirect("/checkout/start")


@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id = request.session.get(
        "checkout_subscription_price_id"
    )
    try:
        obj = SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except:
        obj = None
    if checkout_subscription_price_id is None or obj is None:
        return redirect(reverse("pricing"))

    customer_stripe_id = request.user.customer.stripe_id
    base_url = request.scheme + "://" + request.get_host()
    success_url = base_url + reverse("stripe-checkout-end")
    cancel_url = base_url + reverse("pricing", kwargs={"interval": "month"})

    url = helpers.billing.start_checkout_session(
        customer_id=customer_stripe_id,
        success_url=success_url,
        cancel_url=cancel_url,
        price_stripe_id=obj.stripe_id,
    )
    return redirect(url)


def checkout_finalized_view(request):
    return
