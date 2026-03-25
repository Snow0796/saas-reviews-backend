from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analisar_feedback(texto: str) -> dict:
    prompt = f"""
Analise o seguinte feedback de cliente de restaurante ou hotel.
Retorne APENAS um JSON válido, sem markdown, sem explicações, sem backticks.
O JSON deve ter exatamente estas chaves:
- sentimento: "positivo", "neutro" ou "negativo"
- tema: uma palavra do tema principal (atendimento, comida, limpeza, preco, ambiente, agilidade)
- risco: "baixo", "medio" ou "alto"
- resumo: uma frase curta resumindo o feedback

Feedback: "{texto}"
"""
    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    conteudo = resposta.choices[0].message.content.strip()
    print(f"RESPOSTA IA: {conteudo}")
    
    # Remove backticks se vieram
    if conteudo.startswith("```"):
        conteudo = conteudo.split("```")[1]
        if conteudo.startswith("json"):
            conteudo = conteudo[4:]
    
    return json.loads(conteudo)