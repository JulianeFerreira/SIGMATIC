from django.shortcuts import render, redirect
from django.contrib import messages
from apps.base.views import obter_modulos_dinamicos
from .models import PlanoEstrategico
from .forms import PlanoEstrategicoForm

def pdtic_dashboard_view(request):
    if request.method == 'POST':
        form = PlanoEstrategicoForm(request.POST)
        if form.is_valid():
            plano = form.save()
            messages.success(request, f"Plano '{plano.titulo}' salvo com sucesso!")
            return redirect(request.path)
    else:
        form = PlanoEstrategicoForm()

    modulos, _ = obter_modulos_dinamicos()

    contexto = {
        'modulos': modulos,
        'url_atual': request.path,
        'form': form,
        'planos': PlanoEstrategico.objects.all(),
        'status_python': 'EXECUTADA COM SUCESSO!'
    }

    return render(request, "planejamento/pdtic/dashboard.html", contexto)