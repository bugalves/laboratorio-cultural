from django.shortcuts import render
from .models import Clube

def home(request):
    clubes = Clube.objects.all()

    return render(request, 'core/home.html', {
        'clubes': clubes,
        'user': request.user
    })

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def login_view(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:

            if not user.is_superuser and not email.endswith("@ispgaya.pt"):
                error = "Apenas emails @ispgaya.pt são permitidos"
                return render(request, "registration/login.html", {"error": error})

            login(request, user)

            if user.is_superuser:
                return redirect("/admin/")
            else:
                return redirect("/")

        else:
            error = "Credenciais inválidas"

    return render(request, "registration/login.html", {"error": error})
