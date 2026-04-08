from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("Projeto SIGMATIC rodando 🚀")

urlpatterns = [
    path('', home),
]
