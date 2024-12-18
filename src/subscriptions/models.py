import helpers.billing
import datetime
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

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
    subtitle = models.TextField(null=True, blank=True)
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
    order = models.IntegerField(default=-1, help_text="Ordering on Django Pricing Page")
    featured = models.BooleanField(
        default=True, help_text="Featured on Django pricing page"
    )
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    features = models.TextField(
        help_text="Features for plan pricing separated by newline",
        blank=True,
        null=True,
    )

    @property
    def get_features_list(self):
        if not self.features:
            return []
        return [x.strip() for x in self.features.splitlines()]

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
        ordering = ["order", "featured", "-updated"]

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
    order = models.IntegerField(default=-1, help_text="Ordering on Django Pricing Page")
    featured = models.BooleanField(
        default=True, help_text="Featured on Django pricing page"
    )
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def display_features_list(self):
        if not self.subscription:
            return []
        return self.subscription.get_features_list

    @property
    def get_checkout_url(self):
        return reverse("sub-price-checkout", kwargs={"price_id": self.id})

    @property
    def display_sub_name(self):
        if not self.subscription:
            return "Plan"
        return self.subscription.name.title()

    @property
    def display_sub_subtitle(self):
        if not self.subscription:
            return ""
        return self.subscription.subtitle

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
        # only one price for both monthly and annually must be valid
        # other prices must be inactive(non-featured)
        if self.featured and self.subscription:
            qs = SubscriptionPrice.objects.filter(
                subscription=self.subscription, interval=self.interval
            ).exclude(id=self.id)
            # make other prices in same interval(monthly or yearly) and same subscription plan "false"
            qs.update(featured=False)

    def __str__(self) -> str:
        return self.product_stripe_id

    class Meta:
        ordering = ["subscription__order", "order", "featured", "-updated"]


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    TRAILING = "trailing", "Trailing"
    INCOMPLETE = "incomplete", "Incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired", "Incomplete Expired"
    PAST_DUE = "past_due", "Past Due"
    CANCELED = "canceled", "Canceled"
    UNPAID = "unpaid", "Unpaid"
    PAUSED = "paused", "Paused"


class UserSubscriptionQuerySet(models.QuerySet):
    def by_range(self, days_start=7, days_end=120):
        """
        Filters subscriptions based on whether their `current_period_end`
        falls within a specified range of days from the current date.

        Args:
            days_start (int): The number of days from the current date to start the range.
                              Defaults to 7 days.
            days_end (int): The number of days from the current date to end the range.
                            Defaults to 120 days.

        Returns:
            QuerySet: A queryset of subscriptions where the `current_period_end`
                      is between the start and end of the specified range of days
                      from the current date.
        """
        now = timezone.now()
        days_start_from_now = now + datetime.timedelta(days=days_start)
        days_end_from_now = now + datetime.timedelta(days=days_end)
        range_start = days_start_from_now.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        range_end = days_end_from_now.replace(
            hour=23, minute=59, second=59, microsecond=59
        )
        return self.filter(
            current_period_end__gte=range_start,
            current_period_end__lte=range_end,
        )

    def by_days_left(self, days_left=7):
        """
        Filters subscriptions that have a current_period_end date
        within a specific number of days from the current time.

        Args:
            days_left (int): The number of days from the current date to filter by.
                              Defaults to 7 days.

        Returns:
            QuerySet: A queryset of subscriptions where the current_period_end
                      is between the start and end of the day after the specified
                      number of days from now.
        """
        now = timezone.now()
        in_n_days = now + datetime.timedelta(days=days_left)
        day_start = in_n_days.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = in_n_days.replace(hour=23, minute=59, second=59, microsecond=59)
        return self.filter(
            current_period_end__gte=day_start,
            current_period_end__lte=day_end,
        )

    def by_days_ago(self, days_ago=3):
        """
        Filters subscriptions where the current_period_end date
        is within a specific number of days in the past.

        Args:
            days_ago (int): The number of days in the past to filter by.
                            Defaults to 3 days.

        Returns:
            QuerySet: A queryset of subscriptions where the current_period_end
                      is between the start and end of the day a given number
                      of days ago from the current time.
        """
        now = timezone.now()
        in_n_days = now - datetime.timedelta(days=days_ago)
        day_start = in_n_days.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = in_n_days.replace(hour=23, minute=59, second=59, microsecond=59)
        return self.filter(
            current_period_end__gte=day_start,
            current_period_end__lte=day_end,
        )

    def by_active_trialing(self):
        """
        Filters subscriptions that are either active or in a trialing status.

        Returns:
            QuerySet: A queryset of subscriptions that are either in
                      'ACTIVE' or 'TRIALING' status.
        """
        active_qs_lookup = Q(status=SubscriptionStatus.ACTIVE) | Q(
            status=SubscriptionStatus.TRAILING
        )
        return self.filter(active_qs_lookup)

    def by_user_ids(self, user_ids=None):
        """
        Filters subscriptions based on one or more user IDs.

        Args:
            user_ids (list, int, str, optional): The user ID(s) to filter by.
                                                  Can be a list of IDs or a single ID.

        Returns:
            QuerySet: A queryset of subscriptions where the user_id matches one
                      of the provided IDs. If no valid `user_ids` is provided,
                      it returns the original queryset.
        """
        if isinstance(user_ids, list):
            return self.filter(user_id__in=user_ids)
        elif isinstance(user_ids, int) or isinstance(user_ids, str):
            return self.filter(user_id__in=[user_ids])
        return self


class UserSubscriptionManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return UserSubscriptionQuerySet(self.model, using=self._db)


class UserSubscription(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(
        Subscriptions, on_delete=models.SET_NULL, null=True, blank=True
    )
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    active = models.BooleanField(default=True)
    user_cancelled = models.BooleanField(default=False)
    original_period_start = models.DateTimeField(
        auto_now=False, auto_now_add=False, blank=True, null=True
    )  # track when the user initially subscribed
    current_period_start = models.DateTimeField(
        auto_now=False, auto_now_add=False, blank=True, null=True
    )
    current_period_end = models.DateTimeField(
        auto_now=False, auto_now_add=False, blank=True, null=True
    )
    cancel_at_period_end = models.BooleanField(default=False)
    status = models.CharField(
        null=True,
        blank=True,
        choices=SubscriptionStatus.choices,
        max_length=120
    )

    objects = UserSubscriptionManager()

    def serialize(self):
        """Return dict of current period start, end and the status of the subscription."""
        return {
            "current_period_start": self.current_period_start,
            "current_period_end": self.current_period_end,
            "status": self.status,
            "plan_name": self.plan_name,
        }

    @property
    def is_active_status(self):
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRAILING]

    @property
    def plan_name(self):
        return self.subscription.name if self.subscription else None

    def get_absolute_url(self):
        """Returns the url for account billing (user subscription) view"""
        return reverse("user_subscription")

    def get_cancel_url(self):
        """Returns the url for user subscription cancel view"""
        return reverse("user_subscription_cancel")

    def save(self, *args, **kwargs):
        if self.original_period_start is None and self.current_period_start is not None:
            self.original_period_start = self.current_period_start
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        subscription_data = " - "
        if self.subscription:
            price = self.subscription.subscriptionprice_set.filter(
                featured=True
            ).first()
            if price:
                subscription_data += f"{self.subscription.name} ({price.interval})"

        return self.user.username + subscription_data


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
