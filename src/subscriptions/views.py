from django.shortcuts import render
from subscriptions.models import SubscriptionPrice


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
