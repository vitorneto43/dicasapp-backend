import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis do .env
load_dotenv()

# Inicializa app
app = FastAPI(title="API DicasApp", version="2.0.0")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Chave GNews
API_KEY_GNEWS = os.getenv("API_KEY_GNEWS")

@app.get("/")
def home():
    return {"status": "API DicasApp rodando no Render"}

# ---------------------------
# 1️⃣ Endpoint de Tendências
# ---------------------------
@app.get("/trends")
def get_trends():
    try:
        url_gnews = (
            f"https://gnews.io/api/v4/top-headlines?lang=pt&country=br&q=noticias&max=10&apikey={API_KEY_GNEWS}"
        )
        response = requests.get(url_gnews, timeout=10)
        data = response.json()

        tendencias = [item["title"] for item in data.get("articles", [])]

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
        return {"error": f"Erro ao buscar tendências: {str(e)}"}

# ---------------------------
# 2️⃣ Endpoint Gerar Sugestões com OpenAI
# ---------------------------
class EbookRequest(BaseModel):
    tema: str

@app.post("/gerar_sugestoes")
async def gerar_sugestoes(req: EbookRequest):
    try:
        prompt = f"Crie 5 títulos criativos para eBooks sobre o tema: {req.tema}. Responda apenas com a lista."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em marketing digital e criação de eBooks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=300
        )

        sugestoes_texto = response.choices[0].message.content
        sugestoes_lista = [linha.strip("-• ").strip() for linha in sugestoes_texto.split("\n") if linha.strip()]

        return {"tema": req.tema, "sugestoes": sugestoes_lista}

    except Exception as e:
        # Fallback para evitar erro no app
        return {
            "tema": req.tema,
            "sugestoes": [
                "Guia Completo sobre " + req.tema,
                "Como ganhar dinheiro com " + req.tema,
                "Segredos para dominar " + req.tema,
                "Passo a passo para iniciantes em " + req.tema,
                "Estratégias avançadas sobre " + req.tema
            ],
            "erro": f"Erro ao gerar sugestões: {str(e)}"
        }

    





