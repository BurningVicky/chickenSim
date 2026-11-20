from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, FormView
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .mixins import CartorioRequiredMixin, ProdutorRequiredMixin, LoginRequiredMixin
from .models import Animal, Propriedade, Transferencia
from .forms import PropriedadeForm, AnimalForm, TransferenciaCreateForm, TransferenciaDecisaoForm


@login_required
def dashboard_router(request):
    if request.user.is_cartorio:
        return redirect('cartorio_dashboard')
    return redirect('produtor_dashboard')

class CartorioDashboardView(CartorioRequiredMixin, TemplateView):
    template_name = 'cartorio/dashboard_cartorio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_animais'] = Animal.objects.count()
        context['total_propriedades'] = Propriedade.objects.count()
        context['transferencias_pendentes'] = Transferencia.objects.filter(status='pendente').count()
        return context

class ProdutorDashboardView(ProdutorRequiredMixin, TemplateView):
    template_name = 'cartorio/dashboard_produtor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        propriedades = Propriedade.objects.filter(produtor=self.request.user)
        animais = Animal.objects.filter(propriedade_atual__in=propriedades)
        transferencias = Transferencia.objects.filter(solicitante=self.request.user)

        context['propriedades'] = propriedades
        context['animais'] = animais
        context['transferencias'] = transferencias
        return context

class PropriedadeCreateView(CartorioRequiredMixin, ListView):
    model = Propriedade
    template_name = 'cartorio/propriedade_list.html'
    context_object_name = 'propriedades'

    def get_queryset(self):
        return Propriedade.objects.select_related('produtor').order_by('nome')

class PropriedadeListView(CartorioRequiredMixin, ListView):
    model = Propriedade
    template_name = 'cartorio/propriedade_list.html'
    context_object_name = 'propriedades'

    def get_queryset(self):
        return Propriedade.objects.select_related('produtor').order_by('nome')

class PropriedadeCreateView(CartorioRequiredMixin, CreateView):
    model = Propriedade
    form_class = PropriedadeForm
    template_name = 'cartorio/propriedade_form.html'
    sucess_url = reverse_lazy('propriedade_list')


class AnimalListView(CartorioRequiredMixin, ListView):
    model = Animal
    template_name = 'cartorio/animal_list.html'
    context_object_name = 'animais'

    def get_querset(self):
        qs = Animal.objects.select_related(
            'raca', 'propriedade_atual', 'propriedade_atual__produtor'
        ).order_by('nome')
        busca = self.request.GET.get('q', '').strip()
        if busca:
            qs = qs.filter(
                Q(numero_registro__icontains=busca) | Q(nome__icontains=busca)
            )
        return qs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(kwargs)
        context['busca'] = self.request.GET.get('q', '').strip()
        return context

class AnimalCreateView(CartorioRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'cartorio/animal_form.html'
    sucess_url = reverse_lazy('animal_list')

class AnimalDetailView(CartorioRequiredMixin, DetailView):
    model = Animal
    template_name = 'cartorio/animal_detail.html'
    context_object_name = 'animal'

    def get_queryset(self):
        return Animal.objects.select_related(
            'raca',
            'propriedade_atual',
            'propriedade_atual__produtor',
            'pai',
            'mae',
        )
    
class AnimalUpdateView(CartorioRequiredMixin, UpdateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'cartorio/animal_form.html'
    sucess_url = reverse_lazy('animal_list')

class TransferenciaCreateView(ProdutorRequiredMixin, CreateView):
    model = Transferencia
    form_class = TransferenciaCreateForm
    template_name = 'cartorio/transferencia_form.html'
    success_url = reverse_lazy('produtor_dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        transferencia = form.save(commit=False)
        transferencia.propriedade_origem = transferencia.animal.propriedade_atual
        transferencia.solicitante = self.request.user
        transferencia.status = 'pendente'
        transferencia.save()
        messages.success(
            self.request,
            f'Solicitação de transferência de "{transferencia.animal.nome}" enviada para análise do cartório.',
        )
        return super().form_valid(form)


class TransferenciaPendenteListView(CartorioRequiredMixin, ListView):
    model = Transferencia
    template_name = 'cartorio/transferencia_pendente_list.html'
    context_object_name = 'transferencias'

    def get_queryset(self):
        return (
            Transferencia.objects.filter(status='pendente')
            .select_related(
                'animal',
                'propriedade_origem',
                'propriedade_destino',
                'solicitante',
            )
            .order_by('created_at')
        )


class TransferenciaDecidirView(CartorioRequiredMixin, FormView):
    form_class = TransferenciaDecisaoForm
    template_name = 'cartorio/transferencia_decidir.html'
    success_url = reverse_lazy('transferencia_pendentes')

    def dispatch(self, request, *args, **kwargs):
        self.transferencia = get_object_or_404(
            Transferencia.objects.select_related(
                'animal',
                'propriedade_origem',
                'propriedade_destino',
                'solicitante',
            ),
            pk=kwargs['pk'],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transferencia'] = self.transferencia
        return context

    def form_valid(self, form):
        if self.transferencia.status != 'pendente':
            messages.warning(
                self.request,
                'Esta transferência já foi avaliada anteriormente.',
            )
            return redirect(self.success_url)

        decisao = form.cleaned_data['decisao']
        motivo = form.cleaned_data['motivo_rejeicao']

        with transaction.atomic():
            if decisao == 'aprovada':
                animal = self.transferencia.animal
                animal.propriedade_atual = self.transferencia.propriedade_destino
                animal.save(update_fields=['propriedade_atual'])

                self.transferencia.status = 'aprovada'
                self.transferencia.motivo_rejeicao = ''
                self.transferencia.data_decisao = timezone.now()
                self.transferencia.save(
                    update_fields=['status', 'motivo_rejeicao', 'data_decisao']
                )
                messages.success(
                    self.request,
                    f'Transferência de "{animal.nome}" aprovada! Propriedade atualizada para {self.transferencia.propriedade_destino.nome}.',
                )
            else:
                self.transferencia.status = 'rejeitada'
                self.transferencia.motivo_rejeicao = motivo
                self.transferencia.data_decisao = timezone.now()
                self.transferencia.save(
                    update_fields=['status', 'motivo_rejeicao', 'data_decisao']
                )
                messages.info(
                    self.request,
                    f'Transferência de "{self.transferencia.animal.nome}" rejeitada.',
                )

        return super().form_valid(form)

class TransferenciaHistoricoListView(LoginRequiredMixin, ListView):
    model = Transferencia
    template_name = 'cartorio/transferencia_historico_list.html'
    context_object_name = 'transferencias'

    def get_queryset(self):
        user = self.request.user
        qs = Transferencia.objects.filter(status='aprovada').select_related(
            'animal',
            'propriedade_origem',
            'propriedade_origem__produtor',
            'propriedade_destino',
            'propriedade_destino__produtor',
            'solicitante',
        )
        if not getattr(user, 'is_cartorio', False):
            qs = qs.filter(
                Q(propriedade_origem__produtor=user)
                | Q(propriedade_destino__produtor=user)
            )
        return qs.order_by('-data_decisao', '-created_at', '-pk')

class AnimalCertidaoDetailView(LoginRequiredMixin, DetailView):
    model = Animal
    template_name = 'cartorio/animal_certidao.html'
    context_object_name = 'animal'

    def get_queryset(self):
        return Animal.objects.select_related(
            'raca',
            'propriedade_atual',
            'propriedade_atual__produtor',
            'pai',
            'mae',
        )

    def dispatch(self, request, *args, **kwargs):
        animal = self.get_object()
        if not getattr(request.user, 'is_cartorio', False):
            produtor_id = getattr(animal.propriedade_atual, 'produtor_id', None)
            if produtor_id != request.user.pk:
                raise PermissionDenied(
                    'Você não tem permissão para emitir a certidão desta galinha.'
                )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['historico_transferencias'] = (
            Transferencia.objects.filter(animal=self.object, status='aprovada')
            .select_related(
                'propriedade_origem',
                'propriedade_origem__produtor',
                'propriedade_destino',
                'propriedade_destino__produtor',
                'solicitante',
            )
            .order_by('data_decisao', 'created_at', 'pk')
        )
        return context