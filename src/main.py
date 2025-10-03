#!/usr/bin/env python3
"""
Assistente VocalCom - Ferramenta para Otimizar Atendimento via Chat
"""

import os
import sys

# Adiciona o diretório pai ao path do Python para permitir importação de 'core'
sys.path.append(os.path.dirname(__file__))

def main():
    """Função principal que inicia o assistente"""
    print("🚀 Iniciando Assistente VocalCom...")
    print("📂 Carregando configurações...")
    
    try:
        # Importa depois de ajustar o path
        from interface.cli import ChatCLI
        
        assistant = ChatCLI()
        print("✅ Sistema carregado com sucesso!")
        input("\n⏎ Pressione Enter para abrir o menu principal...")
        assistant.run()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("\n💡 Verificando estrutura de arquivos...")
        
        # Verifica quais arquivos existem
        current_dir = os.path.dirname(__file__)
        print(f"\n📁 Diretório atual: {current_dir}")
        
        interface_path = os.path.join(current_dir, "interface")
        if os.path.exists(interface_path):
            print("✅ Pasta 'interface' encontrada")
            files = os.listdir(interface_path)
            print(f"📄 Arquivos em interface: {files}")
        else:
            print("❌ Pasta 'interface' não encontrada")
            
        core_path = os.path.join(current_dir, "core")
        if os.path.exists(core_path):
            print("✅ Pasta 'core' encontrada")
            files = os.listdir(core_path)
            print(f"📄 Arquivos em core: {files}")
        else:
            print("❌ Pasta 'core' não encontrada")
        
        input("\n⏎ Pressione Enter para sair...")
    
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()