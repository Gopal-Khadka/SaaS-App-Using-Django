from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def profile_view(request, username=None, *args, **kwargs):
    user = request.user
    # user = User.objects.get(username == username)
    # permissions are defined in given manner:
        #<app_label>.add_<model_name>
        #<app_label>.change<model_name>
        #<app_label>.view_<model_name>
        #<app_label>.delete_<model_name>
    print(user.has_perm("delete_user"))
    profile_user_obj = get_object_or_404(User, username = username)
    return HttpResponse(f"Hello there {username}")

