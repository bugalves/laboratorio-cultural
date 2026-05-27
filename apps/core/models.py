from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

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

    class Meta:
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"

class Laboratorio(models.Model):
    imagem = models.ImageField(upload_to='laboratorio/', blank=True, null=True)
    botao_texto = models.CharField(max_length=100, default="Ver atividades")
    botao_link = models.CharField(max_length=255, default="#")

    class Meta:
        verbose_name = "Laboratório"

class Clube(models.Model):
    TIPOS_CLUBE = [
        ('leitura', 'Leitura'),
        ('teatro', 'Teatro'),
        ('tuna', 'Tuna'),
    ]

    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_CLUBE,
        null=True,
        blank=True
    )
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to='clubes/', blank=True, null=True)

    class Meta:
        verbose_name = "Clube"
        verbose_name_plural = "Clubes Culturais"
    
    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

class Cidade(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"

    def __str__(self):
        return self.nome

class Livro(models.Model):
    titulo = models.CharField(max_length=150)
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE, null=True, blank=True, related_name="livros")
    autor = models.CharField(max_length=100, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    capa = models.ImageField(upload_to='livros/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
        ordering = ['-created_at']

    def __str__(self):
        return self.titulo

class Evento(models.Model):
    titulo = models.CharField(max_length=150)

    descricao = models.TextField(null=True, blank=True)

    data_evento = models.DateField(null=True, blank=True)

    local = models.CharField(max_length=150, null=True, blank=True)

    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tipo_evento = models.CharField(max_length=100, null=True, blank=True)

    imagem = models.ImageField(upload_to='eventos/', null=True, blank=True)

    vagas = models.PositiveIntegerField(default=100)

    participantes = models.ManyToManyField(
        Utilizador,
        blank=True,
        related_name="eventos"
    )

    def inscritos(self):
        return self.participantes.count()

    def vagas_restantes(self):
        return self.vagas - self.participantes.count()

    def lotado(self):
        return self.vagas_restantes() <= 0

class SessaoLeitura(models.Model):
    data_sessao = models.DateField(null=True, blank=True)

    local = models.CharField(max_length=150, null=True, blank=True)

    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    livro = models.ForeignKey(
        Livro,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    vagas = models.PositiveIntegerField(default=20)

    participantes = models.ManyToManyField(
        Utilizador,
        blank=True,
        related_name="sessoes_leitura"
    )

    def inscritos(self):
        return self.participantes.count()

    def vagas_restantes(self):
        return self.vagas - self.participantes.count()

    def lotado(self):
        return self.vagas_restantes() <= 0


class SessaoTeatro(models.Model):
    titulo = models.CharField(max_length=150)

    descricao = models.TextField(null=True, blank=True)

    data_sessao = models.DateField(null=True, blank=True)

    local = models.CharField(max_length=150, null=True, blank=True)

    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    imagem = models.ImageField(upload_to='teatro/', null=True, blank=True)

    vagas = models.PositiveIntegerField(default=50)

    participantes = models.ManyToManyField(
        Utilizador,
        blank=True,
        related_name="sessoes_teatro"
    )

    def inscritos(self):
        return self.participantes.count()

    def vagas_restantes(self):
        return self.vagas - self.participantes.count()

    def lotado(self):
        return self.vagas_restantes() <= 0

class Noticia(models.Model):
    titulo = models.CharField(max_length=150)
    conteudo = models.TextField(blank=True, null=True)
    data_publicacao = models.DateField(null=True, blank=True)
    imagem = models.ImageField(upload_to='noticias/', blank=True, null=True)

    clube = models.ForeignKey(Clube, on_delete=models.CASCADE, related_name='noticias', null=True, blank=True)

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"

    def __str__(self):
        return self.titulo

class Galeria(models.Model):
    legenda = models.CharField(max_length=150, blank=True, null=True)
    imagem = models.ImageField(upload_to='galeria/', blank=True, null=True)

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Galeria"

    def __str__(self):
        return self.legenda
    