from django.urls import path

from .views import(
    CartorioDashboardView,
    ProdutorDashboardView,
    PropriedadeCreateView,
    PropriedadeListView,
    AnimalListView,
    AnimalCreateView,
    AnimalDetailView,
    AnimalUpdateView,
    TransferenciaCreateView,
    TransferenciaPendenteListView,
    TransferenciaDecidirView,
    TransferenciaHistoricoListView,
    dashboard_router,
)

urlpatterns = [

    path('', dashboard_router, name='dashboard_router'),
    path('painel/cartorio/', CartorioDashboardView.as_view(), name='cartorio_dashboard'),
    path('painel/produtor/', ProdutorDashboardView.as_view(), name='produtor_dashboard'),
    path('propriedades/', PropriedadeListView.as_view(), name='propriedade_list'),
    path('propriedades/nova/', PropriedadeCreateView.as_view(), name='propriedade_create'),
    path('galinhas/', AnimalListView.as_view(), name='animal_list'),
    path('galinhas/nova/', AnimalCreateView.as_view(), name='animal_create'),
    path('galinhas/<int:pk>/', AnimalDetailView.as_view(), name='animal_detail'),
    path('galinhas/<int:pk>/editar/', AnimalUpdateView.as_view(), name='animal_update'),
    path('transferencias/nova/', TransferenciaCreateView.as_view(), name='transferencia_create'),
    path('transferencias/pendentes/', TransferenciaPendenteListView.as_view(), name='transferencia_pendentes'),
    path('transferencias/<int:pk>/decidir/', TransferenciaDecidirView.as_view(), name='transferencia_decidir'),
    path('transferencias/historico/', TransferenciaHistoricoListView.as_view(), name='transferencia_historico'),
]