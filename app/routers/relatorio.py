from fastapi import APIRouter, HTTPException, Depends
from app.database import supabase
from app.auth import verificar_token
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

def gerar_relatorio_ia(feedbacks: list, nome_ciclo: str, nome_negocio: str) -> str:
    total = len(feedbacks)
    positivos = len([f for f in feedbacks if f["sentimento"] == "positivo"])
    neutros = len([f for f in feedbacks if f["sentimento"] == "neutro"])
    negativos = len([f for f in feedbacks if f["sentimento"] == "negativo"])
    altos_riscos = [f for f in feedbacks if f["risco"] == "alto"]
    
    temas = {}
    for f in feedbacks:
        temas[f["tema"]] = temas.get(f["tema"], 0) + 1
    temas_ordenados = sorted(temas.items(), key=lambda x: x[1], reverse=True)
    
    textos = "\n".join([f'- [{f["sentimento"].upper()} / {f["tema"]} / risco {f["risco"]}]: {f["texto"]}' for f in feedbacks])
    
    prompt = f"""
Você é um consultor sênior de experiência do cliente especializado em hospitalidade.
Analise os feedbacks do negócio "{nome_negocio}" no período "{nome_ciclo}" e escreva um relatório executivo.

DADOS DO PERÍODO:
- Total de feedbacks: {total}
- Positivos: {positivos} ({round(positivos/total*100)}%)
- Neutros: {neutros} ({round(neutros/total*100)}%)
- Negativos: {negativos} ({round(negativos/total*100)}%)
- Temas mais citados: {', '.join([f'{t[0]} ({t[1]}x)' for t in temas_ordenados[:5]])}
- Feedbacks de alto risco: {len(altos_riscos)}

FEEDBACKS COMPLETOS:
{textos}

INSTRUÇÕES:
Escreva um relatório executivo CURTO e DIRETO. Máximo 400 palavras. Estrutura obrigatória:

**PULSO DO PERÍODO — uma frase**
Uma frase única e honesta que define o momento do negócio. Sem rodeios.

**O QUE ESTÁ FUNCIONANDO**
2-3 bullets. Cada bullet: ponto forte + por que ele importa para o negócio.

**ONDE ESTÁ O PROBLEMA REAL**
2-3 bullets. Vá além do sintoma — aponte a causa raiz.
Se houver feedbacks de alto risco, destaque-os aqui com impacto claro.

**3 AÇÕES PARA ESTA SEMANA**
Numeradas. Cada ação: o quê fazer + como medir. Seja específico, nunca genérico.

**TAKE FINAL**
2-3 frases. Sua leitura mais honesta. O que os dados revelam que o gestor precisa ouvir.

Tom: direto, respeitoso, baseado em evidências. Sem eufemismos. Sem enrolação.
Idioma: português brasileiro.
"""

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    
    return resposta.choices[0].message.content

@router.post("/cycles/{cycle_id}/relatorio")
def gerar_relatorio(cycle_id: str, user=Depends(verificar_token)):
    try:
        # Busca tenant
        user_data = supabase.table("users").select("tenant_id").eq("id", user.id).execute()
        tenant_id = user_data.data[0]["tenant_id"]

        # Busca nome do negócio
        tenant_data = supabase.table("tenants").select("nome").eq("id", tenant_id).execute()
        nome_negocio = tenant_data.data[0]["nome"]

        # Busca ciclo
        cycle_data = supabase.table("cycles").select("*").eq("id", cycle_id).eq("tenant_id", tenant_id).execute()
        if not cycle_data.data:
            raise HTTPException(status_code=404, detail="Ciclo não encontrado")
        nome_ciclo = cycle_data.data[0]["nome"]

        # Busca feedbacks do ciclo
        feedbacks = supabase.table("feedbacks").select("*").eq("cycle_id", cycle_id).eq("tenant_id", tenant_id).execute()
        if not feedbacks.data or len(feedbacks.data) == 0:
            raise HTTPException(status_code=400, detail="Nenhum feedback encontrado neste ciclo")

        # Gera relatório
        conteudo = gerar_relatorio_ia(feedbacks.data, nome_ciclo, nome_negocio)

        # Salva no banco
        resultado = supabase.table("reports").insert({
            "tenant_id": tenant_id,
            "cycle_id": cycle_id,
            "conteudo": conteudo
        }).execute()

        return {
            "status": "gerado",
            "ciclo": nome_ciclo,
            "negocio": nome_negocio,
            "total_feedbacks": len(feedbacks.data),
            "relatorio": conteudo
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cycles/{cycle_id}/relatorio")
def buscar_relatorio(cycle_id: str, user=Depends(verificar_token)):
    try:
        user_data = supabase.table("users").select("tenant_id").eq("id", user.id).execute()
        tenant_id = user_data.data[0]["tenant_id"]

        resultado = supabase.table("reports").select("*").eq("cycle_id", cycle_id).eq("tenant_id", tenant_id).order("criado_em", desc=True).limit(1).execute()
        
        if not resultado.data:
            raise HTTPException(status_code=404, detail="Nenhum relatório gerado para este ciclo ainda")

        return {"relatorio": resultado.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))