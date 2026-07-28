# apps/contratacoes/contratos/forms.py
from django import forms
from .models import Contrato

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = '__all__'
        