from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('compras/', views.compras, name='compras'),
    path('contratos/', views.contratos, name='contratos'),
    path('patrimonio/', views.patrimonio, name='patrimonio'),
    path('planejamento/', views.planejamento, name='planejamento'),
]

