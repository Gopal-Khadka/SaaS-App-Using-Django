from django.db import models
from django.contrib.auth.models import Group, Permission

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

    class Meta:
        # custom permissions
        permissions = SUBSCRIPTIONS_PERMS
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self) -> str:
        return self.name
