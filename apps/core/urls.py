from django.urls import path
from . import views

urlpatterns = [
    # Auth Routes
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    # Frontend Routes
    path("", views.home, name="home"),
    path("clubes/<slug:slug>/", views.clube_detail, name="clube_detail"),
    path("programacaocultural/", views.programacaocultural),

    # API Routes
    path("api/user", views.update_user, name="update_user"),
    path("api/calendario-leitura/<slug:slug>/", views.calendario_leitura_json),
    path("api/calendario-teatro/<slug:slug>/", views.calendario_teatro_json),
    path("api/inscrever", views.inscrever),
    path("api/inscricoes/<int:inscricao_id>", views.cancelar_inscricao, name="cancelar_inscricao"),
]