from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("nosotros/", views.nosotros, name="nosotros"),
    path("contacto/", views.contacto, name="contacto"),
    path("terminos/", views.terminos, name="terminos"),
    path("privacidad/", views.privacidad, name="privacidad"),
    path("faq/", views.faq, name="faq"),
    path("soluciones/<slug:slug>/", views.solucion, name="solucion"),
    path("newsletter/", views.newsletter_subscribe, name="newsletter"),
]
