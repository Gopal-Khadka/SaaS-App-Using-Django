import stripe
from decouple import config

DJANGO_DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)
STRIPE_API_KEY = config("STRIPE_API_KEY", cast=str, default=None)
stripe.api_key = STRIPE_API_KEY
if "sk_test" in STRIPE_API_KEY and not DJANGO_DEBUG:
    raise ValueError("Invalid stripe key for production purposes")


def create_customer(name="", email="", metadata={}, raw=False):
    response = stripe.Customer.create(name=name, email=email, metadata=metadata)
    if raw:
        return response
    stripe_id = response.id
    return stripe_id


def create_product(name="", metadata={}, raw=False):
    response = stripe.Product.create(name=name, metadata=metadata)
    if raw:
        return response
    stripe_id = response.id
    return stripe_id


def create_price(
    currency="usd",
    product="",
    unit_amount="9999",
    interval="month",
    metadata={},
    raw=False,
):
    if product is None:
        return None
    response = stripe.Price.create(
        currency=currency,
        unit_amount=unit_amount,
        product=product,
        interval=interval,
        metadata=metadata,
    )

    if raw:
        return response
    stripe_id = response.id
    return stripe_id
