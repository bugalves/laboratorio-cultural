from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse

from .models import (
    Utilizador, Laboratorio, Clube, Cidade,
    Evento, Livro, SessaoLeitura, Noticia, Galeria
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


# ---------------- LABORATORIO ----------------
@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('imagem', 'botao_texto', 'botao_link', 'admin_actions')

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


# ---------------- CLUBE ----------------
@admin.register(Clube)
class ClubeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_criacao', 'admin_actions')
    search_fields = ('nome',)
    list_filter = ('ativo',)

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


# ---------------- EVENTO ----------------
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_evento', 'local', 'tipo_evento', 'admin_actions')
    search_fields = ('titulo', 'local')
    list_filter = ('tipo_evento', 'data_evento')

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


# ---------------- LIVRO ----------------
@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'admin_actions')
    search_fields = ('titulo', 'autor')

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


# ---------------- SESSAO LEITURA ----------------
@admin.register(SessaoLeitura)
class SessaoLeituraAdmin(admin.ModelAdmin):
    list_display = ('data_sessao', 'local', 'clube', 'livro', 'admin_actions')
    list_filter = ('clube',)

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


# ---------------- NOTICIA ----------------
@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_publicacao', 'admin_actions')
    search_fields = ('titulo',)
    list_filter = ('data_publicacao',)

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"


# ---------------- GALERIA ----------------
@admin.register(Galeria)
class GaleriaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'evento', 'admin_actions')
    search_fields = ('titulo',)
    list_filter = ('evento',)

    def admin_actions(self, obj):
        return admin_actions(obj)

    admin_actions.short_description = "Ações"