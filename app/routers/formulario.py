from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import supabase
from app.ia import analisar_feedback

router = APIRouter()

class FeedbackPublico(BaseModel):
    texto: str
    fonte: str = "formulario"
    nome_cliente: str = None
    avaliacao: int = None  # 1 a 5 estrelas

@router.get("/formulario/{tenant_id}")
def info_formulario(tenant_id: str):
    try:
        tenant = supabase.table("tenants").select("nome, segmento").eq("id", tenant_id).eq("ativo", True).execute()
        if not tenant.data:
            raise HTTPException(status_code=404, detail="Formulário não encontrado")
        return {
            "negocio": tenant.data[0]["nome"],
            "segmento": tenant.data[0]["segmento"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/formulario/{tenant_id}")
def enviar_feedback_publico(tenant_id: str, feedback: FeedbackPublico):
    try:
        # Verifica se o tenant existe e está ativo
        tenant = supabase.table("tenants").select("id, nome").eq("id", tenant_id).eq("ativo", True).execute()
        if not tenant.data:
            raise HTTPException(status_code=404, detail="Formulário não encontrado")

        # Busca ciclo ativo do tenant
        ciclo = supabase.table("cycles").select("id").eq("tenant_id", tenant_id).eq("ativo", True).order("criado_em", desc=True).limit(1).execute()
        cycle_id = ciclo.data[0]["id"] if ciclo.data else None

        # Analisa com IA
        analise = analisar_feedback(feedback.texto)

        # Salva feedback
        supabase.table("feedbacks").insert({
            "tenant_id": tenant_id,
            "cycle_id": cycle_id,
            "texto": feedback.texto,
            "fonte": "formulario",
            "sentimento": analise["sentimento"],
            "tema": analise["tema"],
            "risco": analise["risco"],
            "analisado": True
        }).execute()

        return {
            "status": "recebido",
            "mensagem": "Obrigado pelo seu feedback! Sua opinião é muito importante para nós."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))