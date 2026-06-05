from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models import Q

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


# Classe abstrata para definir o atributo vagas e as propriedades de contagem de inscritos, vagas restantes e estado de lotação
# para as 3 entidades que o utilizam, prevenindo código duplicado
class Atividade(models.Model):
    vagas = models.PositiveIntegerField(default=20)

    class Meta:
        abstract = True

    @property
    def inscritos(self):
        return self.inscricoes.count()

    @property
    def vagas_restantes(self):
        return self.vagas - self.inscritos

    @property
    def lotado(self):
        return self.vagas_restantes <= 0


class Evento(Atividade):
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(null=True, blank=True)
    data_evento = models.DateField(null=True, blank=True)
    local = models.CharField(max_length=150, null=True, blank=True)
    tipo_evento = models.CharField(max_length=100, null=True, blank=True)
    imagem = models.ImageField(upload_to='eventos/', null=True, blank=True)

    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


class SessaoLeitura(Atividade):
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


class SessaoTeatro(Atividade):
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(null=True, blank=True)
    data_sessao = models.DateField(null=True, blank=True)
    local = models.CharField(max_length=150, null=True, blank=True)
    imagem = models.ImageField(upload_to='teatro/', null=True, blank=True)

    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


class Inscricao(models.Model):
    utilizador = models.ForeignKey(
        Utilizador,
        on_delete=models.CASCADE
    )

    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inscricoes"
    )

    sessao_leitura = models.ForeignKey(
        SessaoLeitura,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inscricoes"
    )

    sessao_teatro = models.ForeignKey(
        SessaoTeatro,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inscricoes"
    )

    data_inscricao = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def atividade(self):
        return (
            self.evento
            or self.sessao_leitura
            or self.sessao_teatro
        )

    def clean(self):
        campos_preenchidos = sum([
            self.evento is not None,
            self.sessao_leitura is not None,
            self.sessao_teatro is not None,
        ])

        if campos_preenchidos != 1:
            raise ValidationError(
                "A inscrição deve estar associada a exatamente uma atividade."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["utilizador", "evento"],
                name="unique_evento_inscricao"
            ),
            models.UniqueConstraint(
                fields=["utilizador", "sessao_leitura"],
                name="unique_leitura_inscricao"
            ),
            models.UniqueConstraint(
                fields=["utilizador", "sessao_teatro"],
                name="unique_teatro_inscricao"
            ),
            models.CheckConstraint(
            condition=(
                (
                    Q(evento__isnull=False) &
                    Q(sessao_leitura__isnull=True) &
                    Q(sessao_teatro__isnull=True)
                ) |
                (
                    Q(evento__isnull=True) &
                    Q(sessao_leitura__isnull=False) &
                    Q(sessao_teatro__isnull=True)
                ) |
                (
                    Q(evento__isnull=True) &
                    Q(sessao_leitura__isnull=True) &
                    Q(sessao_teatro__isnull=False)
                )
            ),
            name="exactly_one_activity"
        ),
        ]


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
    