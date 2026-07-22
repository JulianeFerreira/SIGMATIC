from django.urls import path
from . import views

urlpatterns = [
    # A string vazia '' pega a raiz exata: /planejamento/pdtic/
    path('', views.pdtic_dashboard_view, name='pdtic_index'),
    path('dashboard/', views.pdtic_dashboard_view, name='pdtic_dashboard'),
]