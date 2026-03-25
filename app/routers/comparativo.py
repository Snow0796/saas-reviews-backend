from fastapi import APIRouter, HTTPException, Depends
from app.database import supabase
from app.auth import verificar_token
from collections import Counter

router = APIRouter()

@router.get("/comparativo")
def comparar_ciclos(user=Depends(verificar_token)):
    try:
        user_data = supabase.table("users").select("tenant_id").eq("id", user.id).execute()
        tenant_id = user_data.data[0]["tenant_id"]

        # Busca todos os ciclos do tenant
        ciclos = supabase.table("cycles").select("*").eq("tenant_id", tenant_id).order("criado_em").execute().data

        if not ciclos:
            return {"comparativo": []}

        resultado = []

        for ciclo in ciclos:
            feedbacks = supabase.table("feedbacks").select("*").eq("cycle_id", ciclo["id"]).eq("tenant_id", tenant_id).execute().data

            total = len(feedbacks)
            if total == 0:
                resultado.append({
                    "ciclo_id": ciclo["id"],
                    "ciclo_nome": ciclo["nome"],
                    "data_inicio": ciclo["data_inicio"],
                    "data_fim": ciclo["data_fim"],
                    "total": 0,
                    "sentimento_score": 0,
                    "positivos": 0,
                    "neutros": 0,
                    "negativos": 0,
                    "alto_risco": 0,
                    "temas_top": []
                })
                continue

            sentimentos = Counter([f["sentimento"] for f in feedbacks])
            temas = Counter([f["tema"] for f in feedbacks if f["tema"]])
            riscos = Counter([f["risco"] for f in feedbacks if f["risco"]])
            sentimento_score = round((sentimentos.get("positivo", 0) / total) * 100)

            resultado.append({
                "ciclo_id": ciclo["id"],
                "ciclo_nome": ciclo["nome"],
                "data_inicio": ciclo["data_inicio"],
                "data_fim": ciclo["data_fim"],
                "total": total,
                "sentimento_score": sentimento_score,
                "positivos": sentimentos.get("positivo", 0),
                "neutros": sentimentos.get("neutro", 0),
                "negativos": sentimentos.get("negativo", 0),
                "alto_risco": riscos.get("alto", 0),
                "temas_top": [{"tema": t, "quantidade": q} for t, q in temas.most_common(3)]
            })

        # Calcula variação entre ciclos consecutivos
        for i in range(1, len(resultado)):
            anterior = resultado[i-1]["sentimento_score"]
            atual = resultado[i]["sentimento_score"]
            variacao = atual - anterior
            resultado[i]["variacao_score"] = variacao
            resultado[i]["tendencia"] = "melhora" if variacao > 0 else "piora" if variacao < 0 else "estavel"

        if resultado:
            resultado[0]["variacao_score"] = 0
            resultado[0]["tendencia"] = "primeiro ciclo"

        return {"comparativo": resultado}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))