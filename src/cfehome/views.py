from django.shortcuts import render
from visits.models import PageVisits


def home_page_view(request):
    queryset = PageVisits.objects.filter(path=request.path)
    my_context = {"title": "Home", "count": queryset.count}
    PageVisits.objects.create(path=request.path)
    return render(request, "home.html", context=my_context)

