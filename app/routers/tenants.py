from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import supabase

router = APIRouter()

class TenantCreate(BaseModel):
    nome: str
    segmento: str
    plano: str = "starter"

@router.post("/tenants")
def criar_tenant(tenant: TenantCreate):
    try:
        resultado = supabase.table("tenants").insert({
            "nome": tenant.nome,
            "segmento": tenant.segmento,
            "plano": tenant.plano
        }).execute()
        return {"status": "criado", "tenant": resultado.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tenants")
def listar_tenants():
    resultado = supabase.table("tenants").select("*").execute()
    return {"tenants": resultado.data}