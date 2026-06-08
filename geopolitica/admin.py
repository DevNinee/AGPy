from django.contrib import admin
# pyrefly: ignore [missing-import]
from .models import Pais, Indicador, BlocoInternacional, PerfilGeopolitico


class IndicadorInline(admin.TabularInline):
    model = Indicador
    extra = 0


class PerfilGeopoliticoInline(admin.StackedInline):
    model = PerfilGeopolitico
    extra = 0


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ['nome', 'regiao', 'codigo_iso2', 'codigo_iso3']
    list_filter = ['regiao']
    search_fields = ['nome']
    inlines = [IndicadorInline, PerfilGeopoliticoInline]


@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):
    list_display = ['pais', 'tipo', 'valor', 'ano', 'fonte', 'categoria']
    list_filter = ['tipo', 'categoria', 'ano', 'fonte']
    search_fields = ['pais__nome']


@admin.register(BlocoInternacional)
class BlocoInternacionalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'sigla']
    list_filter = ['tipo']
    filter_horizontal = ['paises']


@admin.register(PerfilGeopolitico)
class PerfilGeopoliticoAdmin(admin.ModelAdmin):
    list_display = [
        'pais', 'classificacao', 'possui_arsenal_nuclear',
        'membro_conselho_seguranca', 'indice_democracia'
    ]
    list_filter = [
        'classificacao', 'possui_arsenal_nuclear',
        'membro_conselho_seguranca'
    ]
