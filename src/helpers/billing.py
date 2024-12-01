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
        recurring={"interval": interval},
        metadata=metadata,
    )

    if raw:
        return response
    stripe_id = response.id
    return stripe_id


def start_checkout_session(
    success_url="",
    cancel_url="",
    price_stripe_id="",
    customer_id="",
    raw=False,
):
    if not success_url.endswith("?session_id={CHECKOUT_SESSION_ID}"):
        success_url = f"{success_url}" + "?session_id={CHECKOUT_SESSION_ID}"
    response = stripe.checkout.Session.create(
        success_url=success_url,
        cancel_url=cancel_url,
        customer=customer_id,
        line_items=[{"price": price_stripe_id, "quantity": 1}],
        mode="subscription",
    )

    if raw:
        return response
    return response.url
