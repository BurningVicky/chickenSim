from django import forms
from django.contrib.auth.forms import get_user_model

from .models import Propriedade, Animal, Transferencia, Raca


User = get_user_model()


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
        self.fields['produtor'].queryset = User.objects.filter(
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
        numero = (self.cleaned_data.get('numero_registro') or '').strip()
        if not numero:
            raise forms.ValidationError('Informe o número de registro.')

        qs = Animal.objects.filter(numero_registro__iexact=numero)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe uma galinha cadastrada com este número de registro.')
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

class TransferenciaCreateForm(forms.ModelForm):
    class Meta:
        model = Transferencia
        fields = ['animal', 'propriedade_destino', 'observacao']
        labels = {
            'animal': 'Galinha',
            'propriedade_destino': 'Propriedade de Destino',
            'observacao': 'Observação (Opcional)',
        }
        widgets = {
            'animal': forms.Select(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm bg-white',
                }
            ),
            'observacao': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Detalhes da transferência, se necessário.',
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm bg-white',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super() .__init__(*args, (kwargs))
        if self.user is not None:
            propriedades_produtor = Propriedade.objects.filter(produtor=self.user)
            self.fields['animal'].queryset= (
                Animal.objects.filter(propriedade_atual__in=propriedades_produtor)
                .select_related('propriedade_atual', 'raca')
                .order_by('nome')
            )
            self.fields['propriedade_destino'].queryset = Propriedade.objects.exclude(
                produtor=self.user
            ).select_related('produtor').order_by('nome')

    def clean(self):
        cleaned_data = super().clean()
        animal = cleaned_data.get('animal')
        destino = cleaned_data.get('propriedade_destino')

        if animal and destino:
            origem = animal.propriedade_atual
            if origem and origem.pk == destino.pk:
                self.add_error(
                    'propriedade_destino',
                    'A propriedade de destino deve ser diferente da propriedade de origem.',
                )
            if self.user and origem and origem.produtor_id != self.user.pk:
                self.add_error(
                    'animal',
                    'Você só pode solicitar transferência de galinhas em propriedades vinculadas à sua conta.',
                )
        return cleaned_data

class TransferenciaDecisaoForm(forms.Form):
    DECISAO_CHOICES = [
        ('aprovada', 'Aprovar transferência'),
        ('rejeitada', 'Rejeitar transferência'),
    ]

    decisao = forms.ChoiceField(
        label='Decisão do Cartório',
        choices=DECISAO_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'text-slate-900'}),
    )
    motivo_rejeicao = forms.CharField(
        label='Motivo da Rejeição',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'placeholder': 'Obrigatório quando a transferência for rejeitada.',
                'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm bg-white',
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        decisao = cleaned_data.get('decisao')
        motivo = (cleaned_data.get('motivo_rejeicao') or '').strip()

        if decisao == 'rejeitada' and not motivo:
            self.adderror(
                'motivo_rejeicao',
                'Informe o motivo da rejeição para reprovar a transferência.',
            )
        cleaned_data['motivo_rejeicao'] = motivo
        return cleaned_data

class RacaForm(forms.ModelForm):
    class Meta:
        model = Raca
        fields = ['nome']
        labels = {
            'nome': 'Nome da Raça',
        }
        widgets = {
            'nome': forms.TextInput(
                attrs={
                    'placeholder': 'Ex. Rhode Island Red, Brahma...',
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',
                }
            ),
        }

class PropriedadeCartorioForm(forms.ModelForm):
    class Meta:
        model = Propriedade
        fields = ['nome', 'municipio', 'produtor']
        labels = {
            'nome': 'Nome da Propriedade',
            'municipio': 'Município',
            'produtor': 'Produtor Responsável',
        }
        widgets = {
            'nome': forms.TextInput(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',
                }
            ),
            'municipio': forms.TextInput(
                attrs={
                    'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',
                }
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'produtor' in self.fields:
            self.fields['produtor'].queryset = User.objects.filter(
                is_cartorio=False
            ).order_by('username')

class AnimalCartorioForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            'numero_registro',
            'nome',
            'raca',
            'propriedade_atual',
            'pai',
            'mae',
        ]
        labels = {
            'numero_registro': 'Número de Registro',
            'nome': 'Nome da Galinha',
            'raca': 'Raça',
            'propriedade_atual': 'Propriedade do Produtor',
            'pai': 'Pai (Progenitor)',
            'mae': 'Mãe (Progenitora)',
        }
        widgets = {
            'numero+registro': forms.TextInput(
                attrs={'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',}
            ),
            'nome': forms.TextInput(
                attrs={'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',}
            ),
            'raca': forms.Select(
                attrs={'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',}
            ),
            'propriedade_atual': forms.Select(
                attrs={'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',}
            ),
            'pai': forms.Select(
                attrs={'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',}
            ),
            'mae': forms.Select(
                attrs={'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm',}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'propriedade_atual' in self.fields:
            self.fields['propriedade_atual'].queryset = (
                Propriedade.objects.select_related('produtor').order_by('nome')
            )