from django.db import models

class PCAItem(models.Model):
    numero_ordem = models.IntegerField(unique=True, verbose_name="Número de Ordem")
    tipo_item = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tipo de Item")
    descricao_objeto = models.TextField(null=True, blank=True, verbose_name="Descrição Sucinta do Objeto")
    valor_total = models.FloatField(default=0.0, verbose_name="Estimativa de Valor Total")

    def __str__(self):
        return f"Item {self.numero_ordem} - {self.tipo_item}"