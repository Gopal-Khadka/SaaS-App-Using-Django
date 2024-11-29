import helpers.billing
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings

User = settings.AUTH_USER_MODEL
ALLOW_CUSTOM_GROUPS = True
SUBSCRIPTIONS_PERMS = [
    (
        "advanced",
        "Advanced perm",
    ),
    ("pro", "Pro perm"),
    ("basic", "Basic perm"),
    ("basic_ai", "Basic AI perm"),
]


class Subscriptions(models.Model):
    """
    Subscription = Stripe Product
    """

    name = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(
        Permission,
        limit_choices_to={
            "content_type__app_label": "subscriptions",
            # "codename__icontains": "basic",
            "codename__in": [x[0] for x in SUBSCRIPTIONS_PERMS],
        },
    )
    stripe_id = models.CharField(max_length=120, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_id = helpers.billing.create_product(
                name=self.name, metadata={"subscription_plan_id": self.pk}
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)

    class Meta:
        # custom permissions
        permissions = SUBSCRIPTIONS_PERMS
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self) -> str:
        return self.name


class SubscriptionPrice(models.Model):
    """
    Subscription Price = Stripe Price
    """

    class IntervalChoices(models.TextChoices):
        MONTHLY = "month", "Monthly"
        YEARLY = "year", "Yearly"

    subscription = models.ForeignKey(
        Subscriptions, on_delete=models.SET_NULL, null=True
    )
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    interval = models.CharField(
        max_length=120, default=IntervalChoices.MONTHLY, choices=IntervalChoices.choices
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)

    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id

    @property
    def stripe_price(self):
        """Remove decimal places for the price"""
        return int(self.price * 100)

    @property
    def stripe_currency(self):
        return "usd"

    def save(self, *args, **kwargs):
        if self.product_stripe_id is not None and not self.stripe_id:
            stripe_id = helpers.billing.create_price(
                unit_amount=self.stripe_price,
                product=self.product_stripe_id,
                interval=self.interval,
                currency=self.stripe_currency,
                metadata={"subscription_plan_price_id": self.pk},
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.product_stripe_id


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(
        Subscriptions, on_delete=models.SET_NULL, null=True, blank=True
    )
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        subscription_name = self.subscription.name if self.subscription else "None"
        return self.user.username + " - " + subscription_name


def user_sub_post_save(sender, instance, *args, **kwargs):
    """
    Signal handler for the post-save event of the UserSubscription model.

    This function is triggered every time a UserSubscription instance is saved.
    It manages the user's group memberships based on the subscription associated with the UserSubscription.

    It performs the following tasks:
    1. Retrieves the user and the subscription associated with the UserSubscription instance.
    2. Fetches the groups that are linked to the current subscription.
    3. Based on the value of the ALLOW_CUSTOM_GROUPS setting, it either:
        - Replaces the user's current groups with the groups from the subscription, or
        - Merges the user's existing groups with the groups from the subscription, but excludes groups
          from other active subscriptions the user is not subscribed to.

    Specifically, when ALLOW_CUSTOM_GROUPS is True:
    - The user's existing groups are kept, but any groups associated with other active subscriptions (besides the current one)
      are excluded from the user's final group set.

    Args:
        sender (Model): The model class that sent the signal (in this case, UserSubscription).
        instance (UserSubscription): The instance of the UserSubscription model that was saved.
        *args: Additional positional arguments passed by the signal.
        **kwargs: Additional keyword arguments passed by the signal.

    Returns:
        None

    Notes:
        - The ALLOW_CUSTOM_GROUPS setting determines whether the user's existing groups should be preserved.
        - If ALLOW_CUSTOM_GROUPS is True, the function merges the user's current groups with the subscription's groups,
          excluding groups from other active subscriptions the user is not currently subscribed to.
        - If ALLOW_CUSTOM_GROUPS is False, the user's groups are entirely replaced by the subscription's groups.
    """
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription_obj = user_sub_instance.subscription
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list("id", flat=True)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups)
    else:
        groups_ids_set = set(groups_ids)

        subs_qs = Subscriptions.objects.filter(active=True)
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id=subscription_obj.id)
        subs_groups = subs_qs.values_list("groups__id", flat=True)
        subs_groups_set = set(subs_groups)

        current_groups = user.groups.all().values_list("id", flat=True)
        current_groups_set = set(current_groups) - subs_groups_set

        final_group_ids = groups_ids_set | current_groups_set
        user.groups.set(final_group_ids)


post_save.connect(
    user_sub_post_save,
    sender=UserSubscription,
)
