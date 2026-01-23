import os
import io
import edge_tts
import uvicorn
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai

# --- CONFIGURAÇÃO DE DIRETÓRIOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Detecta se está no Render ou Local
IS_RENDER = "RENDER" in os.environ

app = FastAPI(title="Oris - Oração Sincronizada")

# --- CONFIGURAÇÃO DA IA (GEMINI) ---
# Recomendado: Usar variável de ambiente no Render para a chave
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
    """Entrega a Página Inicial (index.html) na RAIZ"""
    path_index = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(path_index):
        return FileResponse(path_index)
    return HTMLResponse(f"Erro: index.html não encontrado na raiz: {path_index}", status_code=404)

@app.get("/mapa.html")
async def read_mapa():
    """Entrega a Página do Mapa em /static"""
    path_mapa = os.path.join(STATIC_DIR, "mapa.html")
    if os.path.exists(path_mapa):
        return FileResponse(path_mapa)
    return HTMLResponse(f"Erro: mapa.html não encontrado na pasta static: {path_mapa}", status_code=404)

# --- ROTA DE SINCRONIZAÇÃO (Ciclo de 15 min: 00, 15, 30, 45) ---
@app.get("/sync")
def sync_clock():
    agora = datetime.datetime.now()
    
    # Lógica para determinar o próximo bloco (00, 15, 30, 45)
    proximo_bloco = ((agora.minute // 15) + 1) * 15
    if proximo_bloco == 60: 
        proximo_bloco = 0
    
    # Cálculo de minutos restantes para o próximo bloco
    minutos_faltam = (proximo_bloco - agora.minute) % 15
    
    # Se estamos exatamente no minuto do bloco (ex: 12:15:05), 
    # faltam 14 minutos e 55 segundos para o próximo (12:30:00)
    if minutos_faltam == 0 and agora.second > 0: 
        minutos_faltam = 15
    
    segundos_restantes = (minutos_faltam * 60) - agora.second
    
    return {"segundos_restantes": segundos_restantes}

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
            "audio_url": f"/static/{audio_filename}?v={datetime.datetime.now().timestamp()}"
        }
    except Exception as e:
        print(f"Erro na geração: {e}")
        return {"texto": "Em harmonia com o todo.", "audio_url": ""}

# --- ROTA DE VOZ DINÂMICA COM VELOCIDADE AJUSTADA ---
@app.get("/api/voice")
async def get_voice(text: str):
    """Gera áudio em tempo real com cadência meditativa (-20%)"""
    try:
        # O parâmetro rate="-20%" torna a fala mais lenta e profunda
        # o rate diminuindo torna a voz mais calma e meditativa
        # communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="-35%")
        # communicate = edge_tts.Communicate(text, "pt-BR-FranciscaNeural", rate="-35%")
        communicate = edge_tts.Communicate(text, "pt-BR-ThalitaNeural", rate="-25%",pitch="-5Hz")
        # communicate = edge_tts.Communicate(text, "pt-BR-FabioNeural", rate="-25%",pitch="-5Hz")
        
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        
        audio_stream.seek(0)
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    except Exception as e:
        print(f"Erro no streaming de voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- REGRAS DE OURO: Mount deve ser a última rota configurada ---
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=not IS_RENDER)