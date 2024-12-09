import helpers.numbers
from django.shortcuts import render

from visits.models import PageVisits
from dashboard.views import dashboard_view


def landing_page_view(request):
    if request.user.is_authenticated:
        return dashboard_view(request)
    qs = PageVisits.objects.all()
    count = qs.count()
    page_views_count = helpers.numbers.shorten_number(count * 100_000)
    social_views_count = helpers.numbers.shorten_number(count * 320_00)
    return render(
        request,
        "landing/main.html",
        {
            "page_views_count": page_views_count,
            "social_views_count": social_views_count,
        },
    )
