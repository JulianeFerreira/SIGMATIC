import uuid  # <-- ADICIONE ESTE IMPORT NO TOPO
from django.db import models
from django.contrib.auth.models import User

# MODEL DE INSTITUIÇÃO
class Instituicao(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome da Instituição")
    sigla = models.CharField(max_length=20, default='', verbose_name="Sigla")
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Instituição"
        verbose_name_plural = "Instituições"

    def __str__(self):
        return f"{self.sigla} - {self.nome}"


# MODEL DE SOLICITAÇÃO DE ACESSO
class SolicitacaoAcesso(models.Model):
    # CHAVE PRIMÁRIA MANTIDA COMO UUID (Evita o erro de conversão no Postgres)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    TIPO_ACESSO_CHOICES = [
        ('ANALISTA', 'Acesso direto a banco de dados (Analista)'),
        ('APLICACAO', 'Usuário de sistema (Conta Técnica/Aplicação)'),
    ]
    
    ORIGEM_CHOICES = [
        ('SESP', 'SESP'),
        ('CELEPAR', 'CELEPAR'),
        ('EXTERNO', 'Órgão Externo / Universidade'),
    ]

    STATUS_CHOICES = [
        ('CRIADA', 'Solicitação Criada'),
        ('EM_ANALISE_DPO', 'Em Análise pelo DPO'),
        ('RECUSADA_DPO', 'Recusada pelo DPO'),
        ('EM_ANALISE_CONTROLADOR', 'Em Análise pelo Controlador'),
        ('CONCLUIDA', 'Solicitação Concluída (Ativo)'),
        ('INATIVO', 'Acesso Revogado (Inativo)'),
    ]

    # 1. DADOS DO SOLICITANTE
    solicitante_sistema = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nome_completo = models.CharField(max_length=200, default='', verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, default='', verbose_name="CPF")
    cargo = models.CharField(max_length=100, default='', verbose_name="Cargo")
    lotacao = models.CharField(max_length=150, default='', verbose_name="Lotação / Departamento")
    email = models.EmailField(default='', verbose_name="E-mail Institucional")
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default='SESP')

    # 2. DADOS TÉCNICOS DA SOLICITAÇÃO
    tipo_acesso = models.CharField(max_length=20, choices=TIPO_ACESSO_CHOICES, default='ANALISTA')
    dados_especificos = models.JSONField(default=dict, verbose_name="Dados Técnicos")

    # 3. TERMOS LEGAIS OBRIGATÓRIOS
    termo_confidencialidade = models.BooleanField(default=False)
    termo_lgpd = models.BooleanField(default=False)

    # 4. FLUXO E GOVERNANÇA
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='CRIADA')
    parecer_dpo = models.TextField(blank=True, null=True, verbose_name="Justificativa DPO em caso de recusa")

    # 5. TRILHA DE AUDITORIA
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitação de Acesso"
        verbose_name_plural = "Solicitações de Acesso"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.nome_completo} - {self.get_tipo_acesso_display()} ({self.get_status_display()})"