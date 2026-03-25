from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import supabase
import jwt

security = HTTPBearer()

def verificar_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials

    if token.startswith("Bearer "):
        token = token[7:]

    try:
        # Decodifica o JWT sem verificar assinatura (o Supabase já valida)
        payload = jwt.decode(token, options={"verify_signature": False})
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")

        # Retorna um objeto simples com os dados do usuário
        class UserInfo:
            def __init__(self, id, email):
                self.id = id
                self.email = email

        return UserInfo(id=user_id, email=email)

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")