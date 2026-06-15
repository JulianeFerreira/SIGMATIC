# apps/base/core/admin.py
from django.contrib import admin
from .models import ModuloSistema

@admin.register(ModuloSistema)
class ModuloSistemaAdmin(admin.ModelAdmin):
    # Quais colunas vão aparecer na lista do painel
    list_display = ('nome', 'slug', 'url_destino', 'ativo')
    
    # Cria um filtro lateral para você buscar rápido os ativos/inativos
    list_filter = ('ativo',)
    
    # Permite pesquisar pelo nome ou slug
    search_fields = ('nome', 'slug')