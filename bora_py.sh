#!/bin/bash

# Nome do script: _start_py.sh
# Descrição: Inicializa o ambiente e o servidor Oris com suporte a Hot-Reload no Linux.

# 1. Definir o caminho do projeto
PROJECT_DIR=$(dirname "$(readlink -f "$0")")
cd "$PROJECT_DIR"

echo "==========================================="
echo "      🌀 ORIS GLOBAL - MODO DESENVOLVIMENTO"
echo "==========================================="

# 2. Verificar e Ativar o Ambiente Virtual
if [ -d "venv" ]; then
    echo "[INFO] Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "[ERRO] Ambiente virtual 'venv' não encontrado."
    exit 1
fi

# 3. Limpeza de Cache (Opcional, mas ajuda no desenvolvimento)
# Remove áudios antigos da pasta static para não ocupar espaço no Linux
#if [ -d "static" ]; then
#    echo "[INFO] Limpando áudios temporários antigos..."
#    rm -f static/*.mp3
#else
#    echo "[INFO] Criando pasta 'static'..."
#    mkdir static
#fi

# 4. Iniciar o servidor
# Como o app.py agora tem o bloco 'if __name__ == "__main__"', 
# basta chamar o python direto. O reload automático já está configurado no app.py!
echo "-------------------------------------------"
echo "✅ SERVIDOR LOCAL: http://127.0.0.1:8000"
echo "✅ RENDER (REF): https://orisglobal.onrender.com"
echo "-------------------------------------------"
echo "[DICA] Qualquer alteração no app.py reiniciará o servidor automaticamente."
echo "Pressione CTRL+C para encerrar."
echo "-------------------------------------------"

python3 app.py
