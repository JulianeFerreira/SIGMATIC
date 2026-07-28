from django import forms
from .models import SolicitacaoAcesso

class SolicitacaoAcessoForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoAcesso
        # Campos que são fixos para QUALQUER tipo de solicitação
        fields = [
            'nome_completo', 'cpf', 'cargo', 'lotacao', 'email', 
            'origem', 'tipo_acesso', 'termo_confidencialidade', 'termo_lgpd'
        ]
        
    def clean(self):
        cleaned_data = super().clean()
        termo_confidencialidade = cleaned_data.get('termo_confidencialidade')
        termo_lgpd = cleaned_data.get('termo_lgpd')

        # Validação pesada: Ninguém passa sem aceitar os termos!
        if not termo_confidencialidade or not termo_lgpd:
            raise forms.ValidationError("Você deve aceitar o Termo de Confidencialidade e a LGPD para prosseguir.")
            
        return cleaned_data