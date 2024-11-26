from django.shortcuts import render,HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from visits.models import PageVisits

LOGIN_URL = settings.LOGIN_URL


def home_page_view(request):
    print(LOGIN_URL)
    queryset = PageVisits.objects.filter(path=request.path)
    my_context = {"title": "Home", "count": queryset.count}
    PageVisits.objects.create(path=request.path)
    return render(request, "home.html", context=my_context)


VALID_CODE = "abc123"


def secret_view(request):
    """This is made to test passcode protected view."""
    is_allowed = request.session.get("protected_page_allowed") or 0
    if request.method == "POST":
        user_pw_sent = request.POST.get("code") or None
        if user_pw_sent == VALID_CODE:
            is_allowed = 1
            request.session["protected_page_allowed"] = is_allowed
    if is_allowed:
        return render(request, "protected/view.html")
    return render(request, "protected/entry.html")


@login_required
def users_only_view(request, *args, **kwargs):
    return render(request, "protected/user-only.html")

def blank_page():
    return HttpResponse("You are not staff")

@staff_member_required(login_url=LOGIN_URL)
def staff_only_view(request, *args, **kwargs):
    return render(request, "protected/staff-only.html")
