from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from django.views.generic import TemplateView, CreateView, ListView

from .mixins import CartorioRequiredMixin, ProdutorRequiredMixin
from .models import Animal, Propriedade, Transferencia

from .forms import PropriedadeForm

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
