from django.urls import path
from .views import login_view, home, clube_detail, programacaocultural, eventos_json

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("programacaocultural/", programacaocultural, name="programacaocultural"),
    path("clubes/<slug:slug>/", clube_detail, name="clube_detail"),
    path("api/eventos/", eventos_json)
]
