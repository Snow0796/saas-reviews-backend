from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tenants, users, feedbacks, cycles, relatorio, metricas, comparativo, formulario

app = FastAPI(
    title="SaaS Reviews API",
    description="API de inteligência de reviews para restaurantes e hotéis",
    version="1.0.0"
)

# CORS — permite o frontend acessar o backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://saas-reviews-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenants.router, prefix="/api/v1", tags=["Tenants"])
app.include_router(users.router, prefix="/api/v1", tags=["Autenticação"])
app.include_router(feedbacks.router, prefix="/api/v1", tags=["Feedbacks"])
app.include_router(cycles.router, prefix="/api/v1", tags=["Ciclos"])
app.include_router(relatorio.router, prefix="/api/v1", tags=["Relatório"])
app.include_router(metricas.router, prefix="/api/v1", tags=["Métricas"])
app.include_router(comparativo.router, prefix="/api/v1", tags=["Comparativo"])
app.include_router(formulario.router, prefix="/api/v1", tags=["Formulário Público"])

@app.get("/")
def root():
    return {"status": "ok", "mensagem": "API rodando com sucesso!"}
    @app.get("/debug")
def debug():
    import os
    return {
        "supabase_url": os.getenv("SUPABASE_URL", "NAO ENCONTRADA"),
        "supabase_key_inicio": os.getenv("SUPABASE_KEY", "NAO ENCONTRADA")[:20],
        "service_key_inicio": os.getenv("SUPABASE_SERVICE_KEY", "NAO ENCONTRADA")[:20],
        "openai_key_inicio": os.getenv("OPENAI_API_KEY", "NAO ENCONTRADA")[:20],
    }