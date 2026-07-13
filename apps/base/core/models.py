# apps/base/core/models.py
from django.db import models

class ModuloSistema(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Módulo")
    
    slug = models.SlugField(unique=True, help_text="Nome usado na URL, sem espaços.")
    
    url_destino = models.URLField(verbose_name="URL de Destino")
    
    ativo = models.BooleanField(default=True, verbose_name="Módulo Ativo?")
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Módulo do Sistema"
        verbose_name_plural = "Módulos do Sistema"

    def __str__(self):
        return f"{self.nome} ({'Ativo' if self.ativo else 'Inativo'})"