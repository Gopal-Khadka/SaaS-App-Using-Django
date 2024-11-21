from django.shortcuts import render


def home_page_view(request):
    my_context = {"title": "Home"}
    return render(request, "home.html", context=my_context)
