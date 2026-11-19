from django.urls import path

from .views import(
    CartorioDashboardView,
    ProdutorDashboardView,
    PropriedadeCreateView,
    PropriedadeListView,
    dashboard_router,
)

urlpatterns = [
    path('', dashboard_router, name='dashboard_router'),
    path('painel/cartorio/', CartorioDashboardView.as_view(), name='cartorio_dashboard'),
    path('painel/produtor/', ProdutorDashboardView.as_view(), name='produtor_dashboard'),
    path('propriedades/', PropriedadeListView.as_view(), name='propriedade_list'),
    path('propriedades/nova/', PropriedadeCreateView.as_view(), name='propriedade_create')
]