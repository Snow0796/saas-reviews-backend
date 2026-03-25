from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import supabase

router = APIRouter()

class UserRegister(BaseModel):
    email: str
    password: str
    nome: str
    tenant_id: str

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/auth/cadastro")
def cadastrar_usuario(user: UserRegister):
    try:
        # Cria o usuário no Supabase Auth
        resultado = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })

        if not resultado.user:
            raise HTTPException(status_code=400, detail="Erro ao criar usuário")

        # Salva informações extras na tabela users
        supabase.table("users").insert({
            "id": resultado.user.id,
            "tenant_id": user.tenant_id,
            "email": user.email,
            "nome": user.nome,
            "role": "admin"
        }).execute()

        return {
            "status": "criado",
            "user_id": resultado.user.id,
            "email": resultado.user.email
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/login")
def login(user: UserLogin):
    try:
        resultado = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })

        return {
            "status": "autenticado",
            "access_token": resultado.session.access_token,
            "user_id": resultado.user.id,
            "email": resultado.user.email
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")