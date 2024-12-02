import helpers.billing
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from subscriptions.models import SubscriptionPrice, UserSubscription


@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    sub_data = user_sub_obj.serialize()
    if request.method == "POST":
        # refresh subscription
        if user_sub_obj.stripe_id:
            sub_data = helpers.billing.get_subscription(user_sub_obj.stripe_id)
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
        return redirect(user_sub_obj.get_absolute_url())

    return render(
        request,
        "subscriptions/user_detail_view.html",
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
