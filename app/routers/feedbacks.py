from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.database import supabase
from app.auth import verificar_token
from app.ia import analisar_feedback

router = APIRouter()

class FeedbackCreate(BaseModel):
    texto: str
    fonte: str
    cycle_id: str = None

@router.post("/feedbacks")
def criar_feedback(feedback: FeedbackCreate, user=Depends(verificar_token)):
    try:
        # Busca o tenant_id do usuário logado
        user_data = supabase.table("users").select("tenant_id").eq("id", user.id).execute()
        tenant_id = user_data.data[0]["tenant_id"]

        # Analisa o feedback com IA
        analise = analisar_feedback(feedback.texto)

        # Salva no banco
        resultado = supabase.table("feedbacks").insert({
            "tenant_id": tenant_id,
            "cycle_id": feedback.cycle_id,
            "texto": feedback.texto,
            "fonte": feedback.fonte,
            "sentimento": analise["sentimento"],
            "tema": analise["tema"],
            "risco": analise["risco"],
            "analisado": True
        }).execute()

        return {
            "status": "criado",
            "feedback": resultado.data[0],
            "analise": analise
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/feedbacks")
def listar_feedbacks(user=Depends(verificar_token)):
    try:
        user_data = supabase.table("users").select("tenant_id").eq("id", user.id).execute()
        tenant_id = user_data.data[0]["tenant_id"]

        resultado = supabase.table("feedbacks").select("*").eq("tenant_id", tenant_id).execute()
        return {"feedbacks": resultado.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))