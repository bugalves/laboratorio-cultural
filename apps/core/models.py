from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UtilizadorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email obrigatório")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class Utilizador(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    NIVEIS = [
        ('admin', 'Admin'),
        ('moderador', 'Moderador'),
        ('user', 'User'),
    ]

    nivel = models.CharField(max_length=20, choices=NIVEIS, default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UtilizadorManager()

class Laboratorio(models.Model):
    nome = models.CharField(max_length=100)
    apresentacao = models.TextField(blank=True, null=True)
    missao = models.TextField(blank=True, null=True)
    objetivos = models.TextField(blank=True, null=True)
    imagem = models.CharField(max_length=255, blank=True, null=True)

class Clube(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

class Cidade(models.Model):
    nome = models.CharField(max_length=100)

class Livro(models.Model):
    titulo = models.CharField(max_length=150)
    autor = models.CharField(max_length=100, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    capa = models.CharField(max_length=255, blank=True, null=True)

class Evento(models.Model):
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)
    data_evento = models.DateField(null=True, blank=True)
    local = models.CharField(max_length=150, blank=True, null=True)
    tipo_evento = models.CharField(max_length=100, blank=True, null=True)
    imagem = models.CharField(max_length=255, blank=True, null=True)

    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE, null=True, blank=True)

class SessaoLeitura(models.Model):
    data_sessao = models.DateField(null=True, blank=True)
    local = models.CharField(max_length=150, blank=True, null=True)

    livro = models.ForeignKey(Livro, on_delete=models.SET_NULL, null=True, blank=True)
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE, null=True, blank=True)


class Noticia(models.Model):
    titulo = models.CharField(max_length=150)
    conteudo = models.TextField(blank=True, null=True)
    data_publicacao = models.DateField(null=True, blank=True)
    imagem = models.CharField(max_length=255, blank=True, null=True)

    clube = models.ForeignKey(Clube, on_delete=models.CASCADE, null=True, blank=True)

class Galeria(models.Model):
    titulo = models.CharField(max_length=150, blank=True, null=True)
    caminho_imagem = models.CharField(max_length=255)

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=True, blank=True)