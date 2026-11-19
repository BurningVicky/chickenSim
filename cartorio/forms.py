from django import forms
from django.contrib.auth.forms import get_user_model

from .models import Propriedade

Usuario = get_user_model()


class PropriedadeForm(forms.ModelForm):
    class Meta:
        model = Propriedade
        fields = ['nome', 'municipio', 'produtor']
        labels = {
            'nome': 'Nome da Propriedade',
            'municipio': 'Município',
            'produtor': 'Produtor',
        }
        widgets = {
            'nome': forms.TextInput(
                attrs={
                    'placeholder': 'Ex.: Harvest Moon',
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm'
                }
            ),
            'municipio': forms.TextInput(
                attrs={
                    'placeholder': 'Ex.: Pelotas',
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm'
                }
            ),
            'produtor': forms.Select(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produtor'].queryset = Usuario.objects.filter(
            is_cartorio=False).order_by('username')