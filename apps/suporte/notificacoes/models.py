from django.db import models
from django.contrib.auth.models import User

class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    
    data_criacao = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.titulo