from django.contrib import admin
from .models import Subscriptions, UserSubscription, SubscriptionPrice


class SubscriptionPriceAdmin(admin.TabularInline):
    model = SubscriptionPrice
    readonly_fields = ["stripe_id"]
    extra = 0  # no of extra prices
    can_delete = False


class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionPriceAdmin]
    readonly_fields = ["stripe_id"]
    list_display = ["name", "active"]


admin.site.register(Subscriptions, SubscriptionAdmin)
admin.site.register(UserSubscription)
