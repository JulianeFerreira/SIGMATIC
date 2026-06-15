# apps/base/core/models.py
from django.db import models

class ModuloSistema(models.Model):
    # O nome bonito do módulo (ex: "Módulo de Compras")
    nome = models.CharField(max_length=100, verbose_name="Nome do Módulo")
    
    # O nome que vai na URL (ex: "compras", "licitacoes")
    slug = models.SlugField(unique=True, help_text="Nome usado na URL, sem espaços.")
    
    # O endereço real de onde o módulo está rodando (ex: http://127.0.0.1:8001)
    url_destino = models.URLField(verbose_name="URL de Destino")
    
    # Um "interruptor" para ligar e desligar o módulo
    ativo = models.BooleanField(default=True, verbose_name="Módulo Ativo?")
    
    # Data de registro (apenas para controle)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Módulo do Sistema"
        verbose_name_plural = "Módulos do Sistema"

    def __str__(self):
        return f"{self.nome} ({'Ativo' if self.ativo else 'Inativo'})"