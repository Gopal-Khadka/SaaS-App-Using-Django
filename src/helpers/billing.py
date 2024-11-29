import stripe
from decouple import config

DJANGO_DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)
STRIPE_API_KEY= config("STRIPE_API_KEY", cast=str, default=None)
stripe.api_key = STRIPE_API_KEY
if "sk_test" in STRIPE_API_KEY and not DJANGO_DEBUG:
    raise ValueError("Invalid stripe key for production purposes")

def create_customer():
    stripe.Customer.create(
        name="Jenny Rosen",
        email="jennyrosen@example.com",
    )
