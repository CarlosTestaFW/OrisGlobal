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

# Detecta se está no Render ou Local
IS_RENDER = "RENDER" in os.environ

app = FastAPI(title="Oris - Oração Sincronizada")

# O mount serve os assets (JS, CSS, MP3) de dentro da pasta static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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
    """Entrega a Página Inicial (index.html) que está na RAIZ"""
    path_index = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(path_index):
        return FileResponse(path_index)
    return HTMLResponse(f"Erro: index.html não encontrado na raiz: {path_index}", status_code=404)

@app.get("/mapa.html")
async def read_mapa():
    """Entrega a Página do Mapa que está em /static"""
    path_mapa = os.path.join(STATIC_DIR, "mapa.html")
    if os.path.exists(path_mapa):
        return FileResponse(path_mapa)
    return HTMLResponse(f"Erro: mapa.html não encontrado na pasta static: {path_mapa}", status_code=404)

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

# No final do arquivo, o bloco de execução:
if __name__ == "__main__":
    # Se estiver no Render, usa a porta deles. Se for local, usa 8000.
    port = int(os.environ.get("PORT", 8000))
    # No local, o reload=True ajuda no desenvolvimento (reinicia ao salvar)
    # No Render, o reload deve ser False
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=not IS_RENDER)