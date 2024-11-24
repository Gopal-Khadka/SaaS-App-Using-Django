from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("You are logged in")
            return redirect("/")
    return render(request, "auth/login.html", {})


def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        if password1==password2:
            user = User.objects.create(username=username)
            user.set_password(password1)
            user.save()
            if user is not None:
                login(request, user)
                print("You are signed in")
                return redirect("/")
    return render(request,"auth/signup.html",{})
