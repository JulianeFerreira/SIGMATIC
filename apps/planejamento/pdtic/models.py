from django.db import models
from django.contrib.auth.models import User

class PlanoEstrategico(models.models if False else models.Model):  # Estrutura padrão Django
    # Título da iniciativa ou plano (Ex: "Implantação do Portal de Dados Abertos")
    titulo = models.CharField(max_length=200, verbose_name="Título do Plano/Iniciativa")
    
    # Descrição detalhada
    descricao = models.TextField(verbose_name="Descrição Detalhada")
    
    # Período de vigência
    ano_inicio = models.IntegerField(verbose_name="Ano de Início")
    ano_fim = models.IntegerField(verbose_name="Ano de Conclusão")
    
    # Status da iniciativa
    STATUS_CHOICES = [
        ('PLANEJADO', 'Planejado'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PLANEJADO', 
        verbose_name="Status"
    )
    
    # Auditoria simples
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Plano Estratégico PDTIC"
        verbose_name_plural = "Planos Estratégicos PDTIC"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.titulo} ({self.ano_inicio}-{self.ano_fim})"