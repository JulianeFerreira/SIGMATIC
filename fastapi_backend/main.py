from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.deps import get_current_user
from app.database import engine, Base
from app.schema_fix import ensure_users_table_has_expected_columns

import os

# ✅ IMPORTANTE:
# Seu projeto usa app/models.py (arquivo). Então NÃO existe app.models.patrimonio.
# Para o create_all criar as tabelas do Patrimônio, precisamos importar o model correto ANTES do create_all.
import app.models
import app.patrimonio_models.patrimonio

# Routers de API (backend) - módulos que já existem no projeto
from app.routers import auth, processos, relatorios, contratos, patrimonio

# ✅ Planejamento pode ainda não existir / estar incompleto (evita crash ao importar)
try:
    from app.routers import planejamento  # type: ignore
except Exception:
    planejamento = None  # fallback seguro

# Ajuste/garantia de schema existente + criação de tabelas
ensure_users_table_has_expected_columns(engine)
Base.metadata.create_all(bind=engine)

# Instância principal da aplicação
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# Arquivos estáticos (CSS, JS, imagens)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates HTML
templates = Jinja2Templates(directory="app/templates")


# ------------------------------------------------------------------
# ROTAS DE INTERFACE - MÓDULO COMPRAS
# ------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def compras_dashboard_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "compras/contratos_dashboard.html",
        {"request": request, "current_user": current_user},
    )


@app.get("/ui/processos", include_in_schema=False)
async def compras_processos_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "compras/processos.html",
        {"request": request, "current_user": current_user},
    )


@app.get("/ui/processos/novo", include_in_schema=False)
async def compras_novo_processo_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "compras/processo_form.html",
        {"request": request, "current_user": current_user},
    )


@app.get("/ui/relatorios", include_in_schema=False)
async def compras_relatorios_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "compras/relatorios.html",
        {"request": request, "current_user": current_user},
    )


@app.get("/ui/processos/{processo_numero}", include_in_schema=False)
async def processo_detail_page(
    request: Request,
    processo_numero: str,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "compras/processo_detail.html",
        {
            "request": request,
            "processo_numero": processo_numero,
            "current_user": current_user,
        },
    )


# ------------------------------------------------------------------
# ROTAS DE INTERFACE - MÓDULO CONTRATOS
# ------------------------------------------------------------------

@app.get("/ui/contratos", include_in_schema=False)
async def contratos_dashboard_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "contratos/contratos_dashboard.html",
        {"request": request, "current_user": current_user},
    )


@app.get("/ui/contratos/lista", include_in_schema=False)
async def contratos_lista_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "contratos/contratos_lista.html",
        {"request": request, "current_user": current_user},
    )


@app.get("/ui/contratos/novo", include_in_schema=False)
async def contratos_novo_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "contratos/contratos_form.html",
        {"request": request, "current_user": current_user},
    )

@app.get("/ui/contratos/acompanhamento", include_in_schema=False)
async def contratos_acompanhamento_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "contratos/contratos_acompanhamento.html",
        {"request": request, "current_user": current_user},
    )

@app.get("/ui/contratos/relatorios", include_in_schema=False)
async def contratos_relatorios_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "contratos/contratos_relatorios.html",
        {"request": request, "current_user": current_user},
    )


# ------------------------------------------------------------------
# ROTA DE INTERFACE - CONFIGURAÇÕES
# ------------------------------------------------------------------

@app.get("/ui/configuracoes", include_in_schema=False)
async def configuracoes_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "configuracoes.html",
        {"request": request, "current_user": current_user},
    )


# ------------------------------------------------------------------
# ROTAS DE INTERFACE - MÓDULO PATRIMÔNIO
# ------------------------------------------------------------------

@app.get("/ui/patrimonio", include_in_schema=False)
async def patrimonio_dashboard_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "patrimonio/contratos_dashboard.html",
        {"request": request, "current_user": current_user},
    )


@app.get("/ui/patrimonio/bens", include_in_schema=False)
async def patrimonio_bens_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "patrimonio/bens_lista.html",
        {"request": request, "current_user": current_user},
    )


@app.get("/ui/patrimonio/bens/novo", include_in_schema=False)
async def patrimonio_bem_novo_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "patrimonio/bem_form.html",
        {"request": request, "current_user": current_user},
    )


@app.get("/ui/patrimonio/bens/{tombamento}", include_in_schema=False)
async def patrimonio_bem_detail_page(
    request: Request,
    tombamento: str,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "patrimonio/bem_detail.html",
        {"request": request, "tombamento": tombamento, "current_user": current_user},
    )


@app.get("/ui/patrimonio/relatorios", include_in_schema=False)
async def patrimonio_relatorios_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        "patrimonio/relatorios.html",
        {"request": request, "current_user": current_user},
    )


# ------------------------------------------------------------------
# ROTAS DE INTERFACE - MÓDULO PLANEJAMENTO (SEGURAS)
# ------------------------------------------------------------------

_PLANEJAMENTO_TEMPLATE = os.path.join("app", "templates", "planejamento", "contratos_dashboard.html")
_PLANEJAMENTO_PCA_TEMPLATE = os.path.join("app", "templates", "planejamento", "pca.html")

if os.path.exists(_PLANEJAMENTO_TEMPLATE):

    @app.get("/ui/planejamento", include_in_schema=False)
    async def planejamento_dashboard_page(
        request: Request,
        current_user=Depends(get_current_user),
    ):
        return templates.TemplateResponse(
            "planejamento/contratos_dashboard.html",
            {"request": request, "current_user": current_user},
        )

if os.path.exists(_PLANEJAMENTO_PCA_TEMPLATE):

    @app.get("/ui/planejamento/pca", include_in_schema=False)
    async def planejamento_pca_page(
        request: Request,
        current_user=Depends(get_current_user),
    ):
        return templates.TemplateResponse(
            "planejamento/pca.html",
            {"request": request, "current_user": current_user},
        )


# ------------------------------------------------------------------
# INCLUIR OS ROUTERS DE API (BACKEND)
# ------------------------------------------------------------------

app.include_router(processos.router)
app.include_router(relatorios.router)
app.include_router(contratos.router)
app.include_router(auth.router)
app.include_router(patrimonio.router)

# Inclui Planejamento somente se o módulo foi importado com sucesso e tem router
if planejamento is not None and hasattr(planejamento, "router"):
    app.include_router(planejamento.router)


# ------------------------------------------------------------------
# RODAR A APLICAÇÃO (caso você execute direto o main.py)
# ------------------------------------------------------------------

if __name__ != "__main__":
    pass
else:
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
