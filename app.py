from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import google.generativeai as genai
import edge_tts
import uvicorn
import os

# --- CONFIGURAÇÃO DE DIRETÓRIOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="Oris - Oração Sincronizada")

# --- CONFIGURAÇÃO DA IA (GEMINI) ---
api_key = os.environ.get("GOOGLE_API_KEY", "AIzaSyDGCEnesZvSDZx4VEs9pYQMMgqC-pcU1pE")
genai.configure(api_key=api_key)
MODEL_NAME = 'models/gemini-1.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

class DadosMeditacao(BaseModel):
    bairro: str
    cidade: str
    nome: str = "Irmão(ã)"

# --- ROTAS DE NAVEGAÇÃO ---

@app.get("/")
async def read_index():
    """Entrega a Página Inicial (index.html)"""
    path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse("Erro: index.html não encontrado na pasta static.", status_code=404)

@app.get("/mapa.html")
async def read_mapa():
    """ROTA FIX: Entrega a Página do Mapa quando acessada diretamente"""
    path = os.path.join(STATIC_DIR, "mapa.html")
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse("Erro: mapa.html não encontrado na pasta static.", status_code=404)

# --- SINCRONIZAÇÃO E IA ---

@app.get("/sync")
def sync_clock():
    agora = datetime.now()
    seg_restantes = 15 - ((agora.hour * 3600 + agora.minute * 60 + agora.second) % 15)
    return {"segundos_restantes": seg_restantes}

@app.post("/gerar-meditacao")
async def gerar_meditacao(dados: DadosMeditacao):
    try:
        prompt = f"Crie uma saudação mística curta para {dados.nome} em {dados.cidade}."
        response = model.generate_content(prompt)
        texto = response.text if response else "Conectando ao fluxo de luz..."
        
        audio_filename = "meditacao.mp3"
        audio_save_path = os.path.join(STATIC_DIR, audio_filename)

        if not os.path.exists(STATIC_DIR):
            os.makedirs(STATIC_DIR)

        communicate = edge_tts.Communicate(texto, "pt-BR-AntonioNeural")
        await communicate.save(audio_save_path)
        
        return {
            "texto": texto, 
            "audio_url": f"/static/{audio_filename}?v={datetime.now().timestamp()}"
        }
    except Exception as e:
        print(f"Erro na geração: {e}")
        return {"texto": "Em harmonia com o todo.", "audio_url": ""}

# O mount fica por último para servir os assets (JS, CSS, MP3) dentro de /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)