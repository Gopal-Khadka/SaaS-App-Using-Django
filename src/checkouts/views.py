import helpers.billing
from django.contrib import messages
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
    """
    Handles the checkout success process after a Stripe session is completed.

    This view retrieves the checkout session details using the session ID from the request,
    extracts customer and subscription information, and updates the user's subscription
    in the database. If the user already has a subscription, the previous one is canceled
    and updated with the new plan.

    Args:
        request (HttpRequest): The HTTP request object containing the session ID.

    Returns:
        HttpResponse: Renders the success page with the updated user subscription details.

    Raises:
        HttpResponseBadRequest: If there is an issue with retrieving the subscription or user information.
    """
    session_id = request.GET.get("session_id")
    checkout_data = helpers.billing.get_checkout_customer_plan(session_id)

    # unpack the checkout data
    customer_id = checkout_data.pop("customer_id")
    plan_id = checkout_data.pop("sub_plan_id")
    sub_stripe_id = checkout_data.pop("sub_stripe_id")
    subscription_data = {**checkout_data}

    try:
        sub_obj = Subscriptions.objects.get(subscriptionprice__stripe_id=plan_id)
    except:
        sub_obj = None

    try:
        user_obj = User.objects.get(customer__stripe_id=customer_id)
    except:
        user_obj = None

    user_sub_exists = False
    updated_sub_options = {
        "subscription": sub_obj,
        "stripe_id": sub_stripe_id,
        "user_cancelled": False,
        **subscription_data,
    }
    try:
        user_sub_obj = UserSubscription.objects.get(user=user_obj)
        user_sub_exists = True

    except UserSubscription.DoesNotExist:
        user_sub_obj = UserSubscription.objects.create(
            user=user_obj, **updated_sub_options
        )
    except:
        user_sub_obj = None

    if None in [sub_obj, user_obj, user_sub_obj]:
        return HttpResponseBadRequest(
            "There was an error with your account, please contact us."
        )

    if user_sub_exists:
        # cancel the old subscription
        old_sub_stripe_id = user_sub_obj.stripe_id
        # check if the new plan is similar to current plan
        same_stripe_id = user_sub_obj.stripe_id == old_sub_stripe_id

        if old_sub_stripe_id is not None and not same_stripe_id:
            cancel_id = helpers.billing.cancel_subscription(
                subscription_id=old_sub_stripe_id,
                reason="Auto ended new membership",
            )
        # assign new subscriptions
        for k, v in updated_sub_options.items():
            setattr(user_sub_obj, k, v)
        user_sub_obj.save()
        messages.success(request,"Success ! Thank you for joining us.")
        return redirect(user_sub_obj.get_absolute_url())


    return render(
        request,
        "checkouts/success.html",
        {"obj": user_sub_obj},
    )
