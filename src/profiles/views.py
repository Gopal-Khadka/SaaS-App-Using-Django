from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def profile_list_view(request):
    context = {"object_list": User.objects.filter(is_active=True)}
    return render(request, "profiles/list.html", context)


@login_required
def profile_detail_view(request, username=None, *args, **kwargs):
    user = request.user
    profile_user_obj = get_object_or_404(User, username=username)
    context = {
        "object": profile_user_obj,
        "owner": profile_user_obj.username == user.username,
    }
    return render(request, "profiles/detail.html", context)