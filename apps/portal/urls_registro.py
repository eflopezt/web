from django.urls import path

from . import views_registro

urlpatterns = [
    path("", views_registro.registro_view, name="registro"),
    path("exito/", views_registro.registro_exito, name="registro_exito"),
]
