#!/usr/bin/env python3
"""
Script de inicialização da Interface Web
"""
import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(__file__))

from backend.app import app

if __name__ == '__main__':
    print("🌐 Iniciando Assistente VocalCom - Interface Web")
    print("📍 Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)