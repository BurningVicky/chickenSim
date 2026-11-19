from django.db.models import Q

from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.shortcuts import redirect

from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView

from .mixins import CartorioRequiredMixin, ProdutorRequiredMixin
from .models import Animal, Propriedade, Transferencia

from .forms import PropriedadeForm, AnimalForm

from django.urls import reverse_lazy


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