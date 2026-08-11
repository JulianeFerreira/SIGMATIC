# apps/contratacoes/contratos/models.py
import uuid
from django.db import models


class Contrato(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_contrato = models.CharField(max_length=100, blank=True, null=True)
    objeto = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False  # Impede o Django de tentar mexer no banco por enquanto
        