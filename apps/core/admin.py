from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilizador, Laboratorio, Clube, Cidade, Evento, Livro, SessaoLeitura, Noticia, Galeria

admin.site.site_header = "Admin ISPGAYA"
admin.site.site_title = "Admin"
admin.site.index_title = "Painel de Gestão"


@admin.register(Utilizador)
class UtilizadorAdmin(UserAdmin):
    model = Utilizador

    list_display = ('email', 'nivel', 'is_staff', 'is_superuser')

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


# 🏛 LABORATÓRIO
@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('nome',)


# 🎭 CLUBES
@admin.register(Clube)
class ClubeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_criacao')
    search_fields = ('nome',)
    list_filter = ('ativo',)


# 🏙 CIDADES
@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


# 📅 EVENTOS
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_evento', 'local', 'tipo_evento')
    search_fields = ('titulo', 'local')
    list_filter = ('tipo_evento', 'data_evento')


# 📚 LIVROS
@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor')
    search_fields = ('titulo', 'autor')


# 📖 SESSÕES DE LEITURA
@admin.register(SessaoLeitura)
class SessaoLeituraAdmin(admin.ModelAdmin):
    list_display = ('data_sessao', 'local', 'clube', 'livro')
    list_filter = ('clube',)


# 📰 NOTÍCIAS
@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_publicacao')
    search_fields = ('titulo',)
    list_filter = ('data_publicacao',)


# 🖼 GALERIA
@admin.register(Galeria)
class GaleriaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'evento')
    search_fields = ('titulo',)
    list_filter = ('evento',)