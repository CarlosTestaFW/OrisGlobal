from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timedelta
import google.generativeai as genai
import edge_tts
import uvicorn
import os

# --- CONFIGURAÇÃO DE DIRETÓRIOS (FIXO PARA LINUX) ---
# Pega o local exato onde este arquivo app.py está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define o caminho da pasta static
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Define os caminhos dos arquivos HTML agora para evitar NameError
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
MAPA_PATH = os.path.join(STATIC_DIR, "mapa.html") # Mapa dentro de /static

app = FastAPI(title="Oris - Oração Sincronizada")

# Cria a pasta static se ela não existir
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# Monta a pasta static para servir áudios e o mapa
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- CONFIGURAÇÃO DA IA (GEMINI) ---
genai.configure(api_key="AIzaSyDGCEnesZvSDZx4VEs9pYQMMgqC-pcU1pE")
MODEL_NAME = 'models/gemini-1.5-flash'
try:
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    print(f"Erro Gemini: {e}")

class DadosMeditacao(BaseModel):
    bairro: str
    cidade: str
    nome: str = "Irmão(ã)"

# --- ROTAS DE NAVEGAÇÃO ---

@app.get("/")
def read_index():
    """Entrega a Página Inicial (na raiz)"""
    if os.path.exists(INDEX_PATH):
        return FileResponse(INDEX_PATH)
    return HTMLResponse(f"Erro: index.html não encontrado em {INDEX_PATH}", status_code=404)

@app.get("/mapa.html")
def read_mapa():
    """Entrega a Página do Mapa (dentro de /static)"""
    if os.path.exists(MAPA_PATH):
        return FileResponse(MAPA_PATH)
    return HTMLResponse(f"Erro: mapa.html não encontrado em {MAPA_PATH}", status_code=404)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return HTMLResponse("", status_code=204)

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

        communicate = edge_tts.Communicate(texto, "pt-BR-AntonioNeural")
        await communicate.save(audio_save_path)
        
        return {
            "texto": texto, 
            "audio_url": f"/static/{audio_filename}?v={datetime.now().timestamp()}"
        }
    except Exception as e:
        print(f"Erro na geração: {e}")
        return {"texto": "Em harmonia com o todo.", "audio_url": ""}

if __name__ == "__main__":
    # Host 0.0.0.0 é melhor para Linux/Docker/Rede Local
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)