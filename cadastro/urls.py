from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_principal, name='menu_principal'),
    path('cadastrar-area/', views.cadastrar_area, name='cadastrar_area'),
    path('cadastrar-cliente/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('cadastrar-equipamento/', views.cadastrar_equipamento, name='cadastrar_equipamento'),
    path('cadastrar-os/', views.cadastrar_ordem_servico, name='cadastrar_ordem_servico'),
    path('fechar-os/', views.fechar_ordem_servico, name='fechar_ordem_servico'),
    path('get-dados-cliente/', views.get_dados_cliente, name='get_dados_cliente'),
    path('registrar-baixa/', views.registrar_baixa_equipamento, name='registrar_baixa_equipamento'),
    path('verificar-cliente/', views.verificar_cliente_existente, name='verificar_cliente'),
    path('verificar-numero-serie/', views.verificar_numero_serie, name='verificar_numero_serie'),
]
