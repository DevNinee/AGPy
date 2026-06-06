from django.contrib import admin
from .models import Pais, Indicador, BlocoInternacional, PerfilGeopolitico


class IndicadorInline(admin.TabularInline):
    """Inline view for Indicador."""
    model = Indicador
    extra = 0


class PerfilGeopoliticoInline(admin.StackedInline):
    """Inline view for PerfilGeopolitico."""
    model = PerfilGeopolitico
    extra = 0


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    """Admin interface for Pais model."""
    list_display = ['nome', 'regiao', 'codigo_iso2', 'codigo_iso3']
    list_filter = ['regiao']
    search_fields = ['nome']
    inlines = [IndicadorInline, PerfilGeopoliticoInline]


@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):
    """Admin interface for Indicador model."""
    list_display = ['pais', 'tipo', 'valor', 'ano', 'fonte', 'categoria']
    list_filter = ['tipo', 'categoria', 'ano', 'fonte']
    search_fields = ['pais__nome']


@admin.register(BlocoInternacional)
class BlocoInternacionalAdmin(admin.ModelAdmin):
    """Admin interface for BlocoInternacional model."""
    list_display = ['nome', 'tipo', 'sigla']
    list_filter = ['tipo']
    filter_horizontal = ['paises']


@admin.register(PerfilGeopolitico)
class PerfilGeopoliticoAdmin(admin.ModelAdmin):
    """Admin interface for PerfilGeopolitico model."""
    list_display = [
        'pais', 'classificacao', 'possui_arsenal_nuclear',
        'membro_conselho_seguranca', 'indice_democracia'
    ]
    list_filter = [
        'classificacao', 'possui_arsenal_nuclear',
        'membro_conselho_seguranca'
    ]
