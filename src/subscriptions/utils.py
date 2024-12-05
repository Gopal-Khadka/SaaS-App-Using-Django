import helpers.billing
from django.db.models import Q
from customers.models import Customer
from subscriptions.models import UserSubscription, Subscriptions, SubscriptionStatus


def refresh_active_users_subscriptions(
    user_ids=None,
    active_only=True,
    days_ago=0,
    days_left=0,
    day_start=0,
    day_end=0,
    verbose=False,
):
    qs = UserSubscription.objects.all()
    if active_only:
        qs = qs.by_active_trialing()
    if user_ids is not None:
        qs = qs.by_user_ids(user_ids=user_ids)

    if days_ago > 0:
        qs = qs.by_days_ago(days_ago=days_ago)
    if days_left > 0:
        qs = qs.by_days_left(days_left=days_left)

    if day_start > 0 and day_end > 0:
        qs = qs.by_range(days_start=day_start, days_end=day_end)

    complete_count = 0
    qs_count = qs.count()
    for obj in qs:
        if verbose:
            print("Updating user", obj.user, obj.subscription, obj.current_period_end)
        if obj.stripe_id:
            sub_data = helpers.billing.get_subscription(obj.stripe_id)
            for k, v in sub_data.items():
                setattr(obj, k, v)
            complete_count += 1
            obj.save()
    return complete_count == qs_count


def clear_dangling_subs():
    """
    This command synchronizes customer subscriptions with their corresponding
    UserSubscription records in the database. It checks for any dangling active
    subscriptions in Stripe (subscriptions that don't have a corresponding
    UserSubscription) and cancels them with the reason 'Dangling active subscriptions'.
    The cancellation can be immediate and does not wait for the subscription to end at the
    end of the billing period or it isn't
    """
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


def sync_subs_group_perms():
    """
    Synchronizes group permissions with subscription permissions.
    This command iterates over all active subscriptions, and for each
    subscription, it sets the permissions of its associated groups to
    match the permissions associated with the subscription. This ensures
    that the groups have the same set of permissions as the subscription,
    keeping the system in sync.
    """
    qs = Subscriptions.objects.filter(active=True)
    for obj in qs:
        sub_perms = obj.permissions.all()
        for group in obj.groups.all():
            group.permissions.set(sub_perms)
            # for perm in obj.permissions.all():
            #     group.permissions.add(perm)
