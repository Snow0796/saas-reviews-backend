from fastapi import APIRouter, HTTPException, Depends
from app.database import supabase
from app.auth import verificar_token
from collections import Counter

router = APIRouter()

@router.get("/cycles/{cycle_id}/metricas")
def metricas_ciclo(cycle_id: str, user=Depends(verificar_token)):
    try:
        user_data = supabase.table("users").select("tenant_id").eq("id", user.id).execute()
        tenant_id = user_data.data[0]["tenant_id"]

        feedbacks = supabase.table("feedbacks").select("*").eq("cycle_id", cycle_id).eq("tenant_id", tenant_id).execute().data

        if not feedbacks:
            return {"total": 0, "mensagem": "Nenhum feedback neste ciclo"}

        total = len(feedbacks)

        # Sentimentos
        sentimentos = Counter([f["sentimento"] for f in feedbacks])
        sentimento_score = round((sentimentos.get("positivo", 0) / total) * 100)

        # Temas
        temas = Counter([f["tema"] for f in feedbacks if f["tema"]])
        temas_lista = [{"tema": t, "quantidade": q, "percentual": round(q/total*100)} for t, q in temas.most_common()]

        # Riscos
        riscos = Counter([f["risco"] for f in feedbacks if f["risco"]])

        # Fontes
        fontes = Counter([f["fonte"] for f in feedbacks if f["fonte"]])
        fontes_lista = [{"fonte": f, "quantidade": q} for f, q in fontes.most_common()]

        # Evolução por dia
        from collections import defaultdict
        por_dia = defaultdict(lambda: {"positivo": 0, "neutro": 0, "negativo": 0, "total": 0})
        for f in feedbacks:
            dia = f["criado_em"][:10]
            por_dia[dia][f["sentimento"]] += 1
            por_dia[dia]["total"] += 1
        evolucao = [{"data": d, **v} for d, v in sorted(por_dia.items())]

        # Feedbacks de alto risco
        alto_risco = [f for f in feedbacks if f["risco"] == "alto"]

        return {
            "total": total,
            "sentimento_score": sentimento_score,
            "sentimentos": {
                "positivo": sentimentos.get("positivo", 0),
                "neutro": sentimentos.get("neutro", 0),
                "negativo": sentimentos.get("negativo", 0)
            },
            "temas": temas_lista,
            "riscos": {
                "alto": riscos.get("alto", 0),
                "medio": riscos.get("medio", 0),
                "baixo": riscos.get("baixo", 0)
            },
            "fontes": fontes_lista,
            "evolucao_diaria": evolucao,
            "alto_risco": alto_risco
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))