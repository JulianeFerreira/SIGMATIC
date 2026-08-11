from django import forms
from .models import PlanoEstrategico

class PlanoEstrategicoForm(forms.ModelForm):
    class Meta:
        model = PlanoEstrategico
        fields = ['titulo', 'descricao', 'ano_inicio', 'ano_fim', 'status']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Implantação do Portal de Dados'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ano_inicio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2026'}),
            'ano_fim': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2028'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }