from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.database import supabase
from app.auth import verificar_token
from typing import Optional

router = APIRouter()

class CycleCreate(BaseModel):
    nome: str
    data_inicio: str
    data_fim: Optional[str] = None

@router.post("/cycles")
def criar_ciclo(cycle: CycleCreate, user=Depends(verificar_token)):
    try:
        user_data = supabase.table("users").select("tenant_id").eq("id", user.id).execute()
        tenant_id = user_data.data[0]["tenant_id"]

        resultado = supabase.table("cycles").insert({
            "tenant_id": tenant_id,
            "nome": cycle.nome,
            "data_inicio": cycle.data_inicio,
            "data_fim": cycle.data_fim,
            "ativo": True
        }).execute()

        return {"status": "criado", "ciclo": resultado.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cycles")
def listar_ciclos(user=Depends(verificar_token)):
    try:
        user_data = supabase.table("users").select("tenant_id").eq("id", user.id).execute()
        tenant_id = user_data.data[0]["tenant_id"]

        resultado = supabase.table("cycles").select("*").eq("tenant_id", tenant_id).execute()
        return {"ciclos": resultado.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/cycles/{cycle_id}/fechar")
def fechar_ciclo(cycle_id: str, user=Depends(verificar_token)):
    try:
        user_data = supabase.table("users").select("tenant_id").eq("id", user.id).execute()
        tenant_id = user_data.data[0]["tenant_id"]

        resultado = supabase.table("cycles").update({"ativo": False}).eq("id", cycle_id).eq("tenant_id", tenant_id).execute()
        return {"status": "fechado", "ciclo": resultado.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))