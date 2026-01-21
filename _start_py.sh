#!/bin/bash

# Nome do script: start_app.sh
# Descrição: Inicializa o ambiente e o servidor FastAPI/Python do projeto Oris.

# 1. Definir o caminho do projeto (diretório onde o script está)
PROJECT_DIR=$(dirname "$(readlink -f "$0")")
cd "$PROJECT_DIR"

echo "==========================================="
echo "   Iniciando Servidor Oris - Backend"
echo "==========================================="

# 2. Verificar se o ambiente virtual existe
if [ -d "venv" ]; then
    echo "[INFO] Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "[ERRO] Ambiente virtual 'venv' não encontrado."
    echo "Certifique-se de estar na pasta correta ou crie o venv com: python3 -m venv venv"
    exit 1
fi

# 3. Garantir que a pasta static existe (necessária para o Edge-TTS)
if [ ! -d "static" ]; then
    echo "[INFO] Criando pasta 'static' para arquivos de áudio..."
    mkdir static
fi

# 4. Iniciar o servidor Python
# Usamos o comando 'python' (que agora aponta para o venv)
echo "[INFO] Servidor rodando em http://127.0.0.1:8000"
echo "Pressione CTRL+C para encerrar."
echo "-------------------------------------------"

python app.py
