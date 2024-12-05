import helpers.billing
from typing import Any
from django.core.management.base import BaseCommand

from customers.models import Customer
from subscriptions.models import UserSubscription


class Command(BaseCommand):
    help = (
        "This command synchronizes customer subscriptions with their corresponding "
        "UserSubscription records in the database. It checks for any dangling active "
        "subscriptions in Stripe (subscriptions that don't have a corresponding "
        "UserSubscription) and cancels them with the reason 'Dangling active subscriptions'. "
        "The cancellation can be immediate and does not wait for the subscription to end at the "
        "end of the billing period or it isn't"
    )

    def handle(self, *args: Any, **options: Any) -> str | None:
        qs = Customer.objects.filter(stripe_id__isnull=False)
        for customer_obj in qs:
            user = customer_obj.user
            customer_stripe_id = customer_obj.stripe_id
            subs = helpers.billing.get_customer_active_subscriptions(customer_stripe_id)
            for sub in subs:
                existing_user_subs_qs = UserSubscription.objects.filter(
                    stripe_id__iexact=f"{sub.id.strip()}"
                )
                if existing_user_subs_qs.exists():
                    continue
                helpers.billing.cancel_subscription(
                    sub.id,
                    reason="Dangling active subscriptions",
                    cancel_at_period_end=False,
                )
                print(sub.id, existing_user_subs_qs.exists())
