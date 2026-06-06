from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse

from .models import (
    Utilizador, Clube, Cidade,
    Evento, Livro, SessaoLeitura, Noticia, SessaoTeatro, Galeria
)

admin.site.site_header = "Admin ISPGAYA"
admin.site.site_title = "Admin"
admin.site.index_title = "Painel de Gestão"


# ---------------- FUNÇÃO REUTILIZÁVEL ----------------
def admin_actions(obj):
    edit = reverse(
        f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
        args=[obj.id]
    )
    delete = reverse(
        f'admin:{obj._meta.app_label}_{obj._meta.model_name}_delete',
        args=[obj.id]
    )

    return format_html(
        '<a class="button" href="{}">Editar</a> '
        '<a class="button" style="color:red;" href="{}">Apagar</a>',
        edit, delete
    )


# ---------------- UTILIZADOR ----------------
@admin.register(Utilizador)
class UtilizadorAdmin(UserAdmin):
    model = Utilizador

    list_display = ('email', 'nivel', 'is_staff', 'is_superuser', 'admin_actions')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissões', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Extra', {'fields': ('nivel',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'nivel', 'is_staff', 'is_superuser'),
        }),
    )

    search_fields = ('email',)
    ordering = ('email',)

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"



# ---------------- CLUBE ----------------
@admin.register(Clube)
class ClubeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_criacao', 'imagem', 'admin_actions')
    search_fields = ('nome',)
    list_filter = ('ativo',)
    prepopulated_fields = {"slug": ("nome",)}

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


# ---------------- CIDADE ----------------
@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'admin_actions')
    search_fields = ('nome',)

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):

    list_display = (
        'titulo',
        'data_evento',
        'local',
        'cidade',
        'tipo_evento',
        'vagas',
        'inscritos',
        'admin_actions'
    )

    readonly_fields = ("lista_participantes",)

    def lista_participantes(self, obj):
        return ", ".join(
            obj.inscricoes.select_related("utilizador")
            .values_list("utilizador__email", flat=True)
        )
    lista_participantes.short_description = "Inscritos"

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"

# ---------------- LIVRO ----------------
@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'admin_actions')

    search_fields = ('titulo', 'autor')

    # REMOVE o campo clube do formulário do admin
    exclude = ('clube',)

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


@admin.register(SessaoLeitura)
class SessaoLeituraAdmin(admin.ModelAdmin):

    list_display = (
        'data_sessao',
        'local',
        'cidade',
        'livro',
        'vagas',
        'inscritos',
        'admin_actions'
    )

    list_filter = ('cidade',)
    search_fields = ('livro__titulo', 'local', 'cidade__nome')

    readonly_fields = ("lista_participantes",)

    def lista_participantes(self, obj):
        return ", ".join(
            obj.inscricoes.select_related("utilizador")
            .values_list("utilizador__email", flat=True)
        )

    lista_participantes.short_description = "Inscritos"

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


@admin.register(SessaoTeatro)
class SessaoTeatroAdmin(admin.ModelAdmin):

    list_display = (
        'titulo',
        'data_sessao',
        'local',
        'cidade',
        'vagas',
        'inscritos',
        'admin_actions'
    )

    list_filter = ('cidade',)
    search_fields = ('titulo', 'local', 'cidade__nome')

    readonly_fields = ("lista_participantes",)

    def lista_participantes(self, obj):
        return ", ".join(
            obj.inscricoes.select_related("utilizador")
            .values_list("utilizador__email", flat=True)
        )

    lista_participantes.short_description = "Inscritos"

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


# ---------------- NOTICIA ----------------
@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_publicacao', 'admin_actions')
    search_fields = ('titulo',)
    list_filter = ('data_publicacao',)

    exclude = ('clube',)

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


@admin.register(Galeria)
class GaleriaAdmin(admin.ModelAdmin):
    list_display = ('legenda', 'imagem', 'acoes')
    search_fields = ('legenda',)

    def acoes(self, obj):
        return admin_actions(obj)

    acoes.short_description = "Ações"
