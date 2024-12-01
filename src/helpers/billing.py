import stripe
from decouple import config
from . import date_utils


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


def get_checkout_session(session_id, raw=False):
    response = stripe.checkout.Session.retrieve(id=session_id)
    if raw:
        return response
    return response.id


def get_subscription(subscription_id, raw=False):
    response = stripe.Subscription.retrieve(id=subscription_id)
    if raw:
        return response
    return response.id


def cancel_subscription(subscription_id, reason="", feedback="other", raw=False):
    response = stripe.Subscription.cancel(
        subscription_id,
        cancellation_details={
            "comment": reason,
            "feedback": feedback,
        },
    )
    if raw:
        return response
    return response.id


def get_checkout_customer_plan(session_id=""):
    """
    Retrieves the subscription details for a customer based on a Stripe Checkout session.

    This function first fetches the checkout session using the provided `session_id`. Then, it retrieves
    the subscription associated with the session and extracts details such as the customer ID, subscription
    plan ID, and subscription start and end dates. The function also converts timestamp values into datetime
    objects for easier handling in the Django model.

    Args:
        session_id (str): The Stripe Checkout session ID. If not provided, an empty string is used, which may
                          result in an error when calling the Stripe API.

    Returns:
        dict: A dictionary containing the following subscription data:
            - "customer_id" (str): The Stripe customer ID.
            - "sub_plan_id" (str): The ID of the subscription plan.
            - "sub_stripe_id" (str): The Stripe subscription ID.
            - "current_period_start" (datetime): The start datetime of the current subscription period.
            - "current_period_end" (datetime): The end datetime of the current subscription period.

    Raises:
        stripe.error.StripeError: If any errors occur while communicating with the Stripe API, such as invalid
                                  session ID or subscription ID.

    Example:
        result = get_checkout_customer_plan("cs_test_1234abcd")   
        print(result)   

         Output:   
         {   
            "customer_id": "cus_abc123xyz",   
           "sub_plan_id": "plan_4567abcd",   
           "sub_stripe_id": "sub_7890xyz",   
           "current_period_start": datetime.datetime(2024, 11, 1, 10, 0, 0),   
           "current_period_end": datetime.datetime(2025, 11, 1, 10, 0, 0),   
         }   
    """

    checkout_r = get_checkout_session(session_id, raw=True)
    customer_id = checkout_r.customer

    sub_stripe_id = checkout_r.subscription
    sub_r = get_subscription(sub_stripe_id, raw=True)
    sub_plan = sub_r.plan

    # convert timestamps into datetime for storing in model
    current_period_start = date_utils.timestamp_as_datetime(sub_r.current_period_start)
    current_period_end = date_utils.timestamp_as_datetime(sub_r.current_period_end)

    # collecting all related data
    data = {
        "customer_id": customer_id,
        "sub_plan_id": sub_plan.id,
        "sub_stripe_id": sub_stripe_id,
        "current_period_start": current_period_start,
        "current_period_end": current_period_end,
    }
    return data
