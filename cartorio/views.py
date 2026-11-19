from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import TemplateView
from .mixins import CartorioRequiredMixin, ProdutorRequiredMixin
from .models import Animal, Propriedade, Transferencia

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