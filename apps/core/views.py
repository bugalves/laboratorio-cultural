from django.shortcuts import render
from .models import Clube, Evento, Galeria, Laboratorio

def home(request):
    clubes = Clube.objects.all()
    eventos = Evento.objects.all()
    galerias = Galeria.objects.all()
    laboratorio = Laboratorio.objects.first()

    return render(request, 'core/home.html', {
        'clubes': clubes,
        'eventos': eventos,
        'galerias': galerias,
        'laboratorio': laboratorio,
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

            if user.is_superuser or user.nivel in ["admin", "moderador"]:
                user.is_staff = True
                user.save()
                return redirect("/admin/")

            return redirect("/")

        else:
            error = "Credenciais inválidas"

    return render(request, "registration/login.html", {"error": error})
