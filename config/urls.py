
from django.contrib import admin
from django.urls import path
from apps.core.views import home, login_view, clubedeleitura, clubedeteatro, programacaocultural

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("clubedeleitura/", clubedeleitura, name="clubedeleitura"),
    path("clubedeteatro/", clubedeteatro, name="clubedeteatro"),
    path("programacaocultural/", programacaocultural, name="programacaocultural"),
    path("admin/", admin.site.urls),
]
