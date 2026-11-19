from django import forms
from django.contrib.auth.forms import get_user_model

from .models import Propriedade, Animal


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


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            'numero_registro',
            'nome',
            'especie',
            'sexo',
            'nascimento',
            'raca',
            'propriedade_atual',
            'pai',
            'mae',
            'status',
        ]
        labels = {
            'numero_registro': 'Número de Registro',
            'nome': 'Nome do Animal',
            'especie': 'Espécie',
            'sexo': 'Sexo',
            'nascimento': 'Data de Nascimento',
            'raca': 'Raça',
            'propriedade_atual': 'Propriedade Atual',
            'pai': 'Pai',
            'mae': 'Mãe',
            'status': 'Status do Animal',
        }
        widgets = {
            'numero_registro': forms.TextInput(
                attrs={
                    'placeholder': 'Ex.: REG-2026-001',
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',
                }
            ),
            'nome': forms.TextInput(
                attrs={
                    'placeholder': 'Ex.: Penélope',
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',
                }
            ),
            'especie': forms.TextInput(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',
                }
            ),
            'sexo': forms.Select(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm bg-white',
                }
            ),
            'nascimento': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',
                }
            ),
            'raca': forms.Select(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm bg-white',
                }
            ),
            'propriedade_atual': forms.Select(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm bg-white',
                }
            ),
            'pai': forms.Select(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm bg-white',
                }
            ),
            'mae': forms.Select(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm bg-white',
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm bg-white',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        animais_qs = Animal.objects.order_by('numero_registro', 'nome')
        if self.instance and self.instance.pk:
            animais_qs = animais_qs.exclude(pk=self.instance.pk)
        self.fields['pai'].queryset = animais_qs.filter(sexo='M')
        self.fields['mae'].queryset = animais_qs.filter(sexo='F')

    def clean_numero_registro(self):
        numero = self.cleaned_data.get['numero_registro'].strip()
        qs = Animal.objects.filter(numero_registro__iecaxt=numero)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                'Já existe uma galinha cadastrada com este número de registro.'
            )
        return numero

    def clean(self):
        cleaned_data = super().clean()
        pai = cleaned_data.get('pai')
        mae = cleaned_data.get('mae')
        if self.instance and self.instance.pk:
            if pai and pai.pk == self.instance.pk:
                self.add_error('pai', 'O pai não pode ser o próprio animal.')
            if mae and mae.pk == self.instance.pk:
                self.add_error('mae', 'A mãe não pode ser o próprio animal.')
        return cleaned_data

