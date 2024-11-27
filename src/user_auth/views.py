from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.views import View

User = get_user_model()
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("You are logged in")
            return redirect("/")
    return render(request, "user_auth/login.html", {})


def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        # validation
        # username_exists_qs = User.objects.filter(username__iexact=username).exists()
        # if username_exists_qs:
        #     print("Username already exists")
        if password1==password2:
            user = User.objects.create_user(username=username,password=password1)
            if user is not None:
                login(request, user)
                print("You are signed in")
                return redirect("/")
    return render(request,"user_auth/signup.html",{})
