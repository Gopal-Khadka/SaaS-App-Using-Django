import helpers.billing
from typing import Any
from django.core.management.base import BaseCommand, CommandParser

from subscriptions import utils as subs_utils


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--clear-dangling", action="store_true", default=False)
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> str | None:
        clear_dangling = options.get("clear_dangling")
        if clear_dangling:
            print("Clearing all dangling active (not in use) subscriptions ...")
            subs_utils.clear_dangling_subs()
            print("Cleared all dangling active subscriptions !!!")
        else:
            print("Refreshing(syncing) active subs...")
            done = subs_utils.refresh_active_users_subscriptions(
                active_only=True, verbose=True
            )
            print("Done !!!" if done else "Failed :(")
