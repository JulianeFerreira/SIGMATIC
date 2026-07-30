from django.contrib import admin
from .models import Instituicao, SolicitacaoAcesso

@admin.register(Instituicao)
class InstituicaoAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('sigla', 'nome')

@admin.register(SolicitacaoAcesso)
class SolicitacaoAcessoAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'origem', 'tipo_acesso', 'status', 'criado_em')
    list_filter = ('status', 'tipo_acesso', 'origem', 'criado_em')
    search_fields = ('nome_completo', 'cpf', 'email', 'lotacao')
    readonly_fields = ('criado_em', 'atualizado_em')