from django import forms
from .models import Doacao

class DonateForm(forms.ModelForm):
    class Meta:
        model = Doacao
        fields = ['nome', 'email', 'telefone', 'cpf', 'valor']
        labels = {
            'nome': 'Nome:',
            'email': 'E-mail:',
            'telefone': 'Telefone:',
            'valor': 'Valor a ser doado:',
            'cpf': 'CPF:',
        }
