from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models import Q
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



class Cidade(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"

    def clean(self):
        self.nome = self.nome.strip().title()

        if Cidade.objects.filter(nome__iexact=self.nome).exclude(pk=self.pk).exists():
            raise ValidationError("Essa cidade já existe.")

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=150)
    clube = models.ForeignKey(
        Clube,
        on_delete=models.PROTECT,
        related_name="livros",
        null=True,
        blank=True
    )

    autor = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    capa = models.ImageField(upload_to='livros/')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.clube_id:
            self.clube = Clube.objects.get(tipo='leitura')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

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

    def clean(self):
        if self.data_evento and self.data_evento < timezone.now().date():
            raise ValidationError("Não podes criar eventos em datas passadas.")



class SessaoLeitura(Atividade):
    data_sessao = models.DateField()
    local = models.CharField(max_length=150)

    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.PROTECT
    )

    livro = models.ForeignKey(
        Livro,
        on_delete=models.PROTECT
    )

def clean(self):
    if self.data_sessao and self.data_sessao < timezone.now().date():
        raise ValidationError(
            "Não podes criar sessões de leitura em datas passadas."
        )



class SessaoTeatro(Atividade):
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(max_length=3000)
    data_sessao = models.DateField()
    local = models.CharField(max_length=150)
    imagem = models.ImageField(upload_to='teatro/')

    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.PROTECT
    )

def clean(self):
    if self.data_sessao and self.data_sessao < timezone.now().date():
        raise ValidationError(
            "Não podes criar sessões de leitura em datas passadas."
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
    conteudo = models.TextField(max_length=5000)
    data_publicacao = models.DateField()
    imagem = models.ImageField(upload_to='noticias/')

    clube = models.ForeignKey(
        Clube,
        on_delete=models.CASCADE,
        related_name='noticias',
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.clube_id:
            self.clube = Clube.objects.get(tipo='teatro')
        super().save(*args, **kwargs)


class Galeria(models.Model):
    legenda = models.CharField(max_length=150, blank=True, null=True)
    imagem = models.ImageField(upload_to='galeria/teatro/')

    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Galeria Teatro"
        verbose_name_plural = "Galeria Teatro"

    def __str__(self):
        return self.legenda or "Imagem Teatro"
