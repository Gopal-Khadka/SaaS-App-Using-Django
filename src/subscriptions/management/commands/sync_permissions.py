from typing import Any
from django.core.management.base import BaseCommand
from subscriptions.models import Subscriptions


class Command(BaseCommand):
    help = (
        "Synchronizes group permissions with subscription permissions. "
        "This command iterates over all active subscriptions, and for each "
        "subscription, it sets the permissions of its associated groups to "
        "match the permissions associated with the subscription. This ensures "
        "that the groups have the same set of permissions as the subscription, "
        "keeping the system in sync."
    )

    def handle(self, *args: Any, **options: Any) -> str | None:
        qs = Subscriptions.objects.filter(active=True)
        for obj in qs:
            # print(obj.name)
            # print(obj.groups.all())
            sub_perms = obj.permissions.all()
            for group in obj.groups.all():
                group.permissions.set(sub_perms)
                # for perm in obj.permissions.all():
                #     group.permissions.add(perm)
            # print(obj.permissions.all())
