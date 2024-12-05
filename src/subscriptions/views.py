import helpers.billing
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from subscriptions.models import SubscriptionPrice, UserSubscription
from subscriptions import utils as sub_utils


@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    sub_data = user_sub_obj.serialize()
    if request.method == "POST":
        # refresh subscription
        finished_refresh = sub_utils.refresh_active_users_subscriptions(
            user_ids=[request.user.id]
        )
        if finished_refresh:
            messages.success(request, "Your current plan details has been refreshed")
        else:
            messages.error(
                request,
                message="Something failed while refreshing the subscription. Try Again !!",
            )
        return redirect(user_sub_obj.get_absolute_url())

    return render(
        request,
        "subscriptions/user_detail_view.html",
        {"subscription": user_sub_obj},
    )


@login_required
def user_subscription_cancel_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    sub_data = user_sub_obj.serialize()
    if request.method == "POST":
        # refresh subscription
        if user_sub_obj.stripe_id and user_sub_obj.is_active_status:
            sub_data = helpers.billing.cancel_subscription(
                user_sub_obj.stripe_id,
                reason="User wanted to end",
                feedback="other",
                cancel_at_period_end=True,
            )
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
            messages.success(request, "Your current plan has been cancelled")
        return redirect(user_sub_obj.get_absolute_url())

    return render(
        request,
        "subscriptions/user_cancel_view.html",
        {"subscription": user_sub_obj},
    )


def subscription_price_view(request, interval="month"):
    inv_month = SubscriptionPrice.IntervalChoices.MONTHLY
    inv_year = SubscriptionPrice.IntervalChoices.YEARLY

    qs = SubscriptionPrice.objects.filter(featured=True)
    object_list = qs.filter(interval=inv_month)
    if interval == inv_year:
        object_list = qs.filter(interval=inv_year)
    return render(
        request,
        "subscriptions/pricing.html",
        {"object_list": object_list},
    )
