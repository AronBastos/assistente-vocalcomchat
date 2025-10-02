import json
import pyperclip
from datetime import datetime
import os

class ChatAssistant:
    def __init__(self, data_dir="../data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.quick_responses = self.load_responses()
        self.conversation_history = []
    
    def load_responses(self):
        """Carrega respostas rápidas de um arquivo JSON"""
        file_path = os.path.join(self.data_dir, "respostas_rapidas.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_responses()
    
    def get_default_responses(self):
        """Retorna respostas padrão"""
        return {
            "saudacao": {
                "message": "Olá! Em que posso ajudar?",
                "category": "inicio"
            },
            "agradecimento": {
                "message": "Obrigado pelo contato! Fico feliz em ajudar.",
                "category": "inicio"
            },
            "problema_rede": {
                "message": "Vou verificar a conectividade de rede do seu setor. Enquanto isso, pode tentar reiniciar o roteador?",
                "category": "rede"
            },
            "senha_bloqueada": {
                "message": "Posso ajudar com o desbloqueio de senha. Precisa que eu reset sua senha agora?",
                "category": "acesso"
            },
            "lentidao": {
                "message": "Entendo que está com lentidão. Vou verificar nossos sistemas. Pode me informar qual aplicação está lenta?",
                "category": "performance"
            },
            "follow_up": {
                "message": "Vou acompanhar este caso e retorno em 30 minutos com atualizações.",
                "category": "acompanhamento"
            }
        }
    
    def save_responses(self):
        """Salva as respostas no arquivo JSON"""
        file_path = os.path.join(self.data_dir, "respostas_rapidas.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.quick_responses, f, ensure_ascii=False, indent=2)
    
    def add_quick_response(self, key, message, category):
        """Adiciona nova resposta rápida"""
        self.quick_responses[key] = {
            "message": message,
            "category": category
        }
        self.save_responses()
        print(f"✅ Resposta '{key}' adicionada com sucesso!")
    
    def get_response(self, key):
        """Recupera uma resposta rápida"""
        if key in self.quick_responses:
            response = self.quick_responses[key]["message"]
            pyperclip.copy(response)
            self.log_conversation(f"Resposta: {key}", response)
            return response
        return None
    
    def search_responses(self, keyword):
        """Busca respostas por palavra-chave"""
        matches = {}
        for key, data in self.quick_responses.items():
            if keyword.lower() in data["message"].lower() or keyword.lower() in key.lower():
                matches[key] = data
        return matches
    
    def log_conversation(self, context, response):
        """Registra o uso para analytics"""
        log_entry = {
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "context": context,
            "response": response
        }
        self.conversation_history.append(log_entry)
        
        # Salva em arquivo
        log_file = os.path.join(self.data_dir, "chat_history.json")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_categories(self):
        """Retorna todas as categorias disponíveis"""
        categories = set()
        for data in self.quick_responses.values():
            categories.add(data["category"])
        return sorted(list(categories))