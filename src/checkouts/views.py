import helpers.billing
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseBadRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from subscriptions.models import SubscriptionPrice, Subscriptions, UserSubscription

User = get_user_model()


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
    session_id = request.GET.get("session_id")
    customer_id, plan_id = helpers.billing.get_checkout_customer_plan(session_id)

    try:
        sub_obj = Subscriptions.objects.get(subscriptionprice__stripe_id=plan_id)
    except:
        sub_obj = None

    try:
        user_obj = User.objects.get(customer__stripe_id=customer_id)
    except:
        user_obj = None

    user_sub_exists = False
    try:
        user_sub_obj = UserSubscription.objects.get(user=user_obj)
        user_sub_exists = True

    except UserSubscription.DoesNotExist:
        user_sub_obj = UserSubscription.objects.create(
            user=user_obj, subscription=sub_obj
        )
    except:
        user_sub_obj = None

    if None in [sub_obj, user_obj, user_sub_obj]:
        return HttpResponseBadRequest(
            "There was an error with your account, please contact us."
        )
    
    if user_sub_exists:
        user_sub_obj.subscription = sub_obj
        user_sub_obj.save()

    print(user_sub_obj)
    return render(
        request,
        "checkouts/success.html",
        {"obj": user_sub_obj},
    )
