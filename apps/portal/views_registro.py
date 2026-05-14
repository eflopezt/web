from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegistroClienteForm


def registro_view(request):
    if request.user.is_authenticated:
        return redirect("portal:dashboard")
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Bienvenido! Tu cuenta de cliente fue creada.")
            return redirect("portal:dashboard")
    else:
        form = RegistroClienteForm()
    return render(request, "portal/registro.html", {"form": form})


def registro_exito(request):
    return render(request, "portal/registro_exito.html")
