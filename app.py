import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

# ✅ Carrega variáveis do .env
load_dotenv()

app = FastAPI(title="API DicasApp", version="1.0.0")

# ✅ Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Variáveis de ambiente
API_KEY_GNEWS = os.getenv("API_KEY_GNEWS")
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
def home():
    return {"status": "API rodando com FastAPI no Render!"}

# --------------------
# 1️⃣ Rota para tendências (GNews)
# --------------------
@app.get("/trends")
def get_trends():
    try:
        url_gnews = (
            f"https://gnews.io/api/v4/top-headlines?lang=pt&country=br&q=noticias&max=10&apikey={API_KEY_GNEWS}"
        )
        response = requests.get(url_gnews)
        data = response.json()

        tendencias = [item["title"] for item in data.get("articles", [])]

        # ✅ Fallback se não houver resultados
        if not tendencias:
            tendencias = [
                "Como ganhar dinheiro online em 2025",
                "Receitas fitness para emagrecer rápido",
                "Estratégias para renda extra usando IA",
                "Organização financeira para iniciantes",
                "Técnicas para reduzir ansiedade",
                "Melhores investimentos de baixo risco",
                "Como trabalhar de casa e lucrar",
                "Guia prático para marketing digital",
                "Como economizar dinheiro em 2025",
                "Passo a passo para vender no Hotmart"
            ]

        return {"fonte": "GNews", "pais": "Brasil", "tendencias": tendencias}

    except Exception as e:
        return {"error": "Erro ao buscar tendências."}

# --------------------
# 2️⃣ Rota para gerar sugestões via IA (OpenAI)
# --------------------
class EbookRequest(BaseModel):
    tema: str

@app.post("/gerar_sugestoes")
async def gerar_sugestoes(req: EbookRequest):
    try:
        prompt = f"Crie 5 títulos criativos para eBooks sobre o tema: {req.tema}"

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em marketing digital e criação de eBooks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=200
        )

        sugestoes_texto = response.choices[0].message["content"]

        # ✅ Limpeza do texto
        sugestoes_lista = [
            linha.replace("-", "").replace("*", "").strip()
            for linha in sugestoes_texto.split("\n")
            if linha.strip()
        ]

        return {"tema": req.tema, "sugestoes": sugestoes_lista}

    except Exception as e:
        return {"error": "Erro ao gerar sugestões, tente novamente mais tarde."}
    

print(f"Erro ao chamar OpenAI: {str(e)}")



