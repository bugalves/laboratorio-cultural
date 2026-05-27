from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("programacaocultural/", views.programacaocultural),

    path("clubes/<slug:slug>/", views.clube_detail, name="clube_detail"),

    path("api/calendario-leitura/<slug:slug>/", views.calendario_leitura_json),
    path("api/calendario-teatro/<slug:slug>/", views.calendario_teatro_json),
    path("participar/<str:tipo>/<int:evento_id>/", views.participar_evento),
]