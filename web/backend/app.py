"""
Backend Flask para Interface Web do Assistente VocalCom
Versão com tratamento de erro melhorado e fallbacks
"""
import sys
import os
import json
from datetime import datetime

# ===== CONFIGURAÇÃO DE IMPORTAÇÕES COM FALLBACK =====
FLASK_AVAILABLE = False
CORE_AVAILABLE = False

# Tenta importar Flask
try:
    from flask import Flask, render_template, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
    print("✅ Flask e dependências carregadas com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Flask: {e}")
    print("💡 Execute: pip install Flask==2.3.3 Flask-CORS==4.0.0")

# Adiciona o path para importar do core existente
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Tenta importar módulos core
try:
    from core.chat_assistant import ChatAssistant
    from core.template_engine import TemplateEngine
    CORE_AVAILABLE = True
    print("✅ Módulos core carregados com sucesso")
except ImportError as e:
    print(f"⚠️  Módulos core não disponíveis: {e}")
    print("💡 Verifique a estrutura do projeto")

# ===== CONFIGURAÇÃO DO APP FLASK =====
if FLASK_AVAILABLE:
    app = Flask(__name__)
    CORS(app)  # Habilita CORS para todas as rotas
    app.secret_key = 'assistente_vocalcom_web_secret_2024'
else:
    # Cria um objeto dummy se Flask não estiver disponível
    class DummyApp:
        def route(self, *args, **kwargs):
            return lambda func: func
        def run(self, *args, **kwargs):
            print("❌ Flask não disponível - não é possível executar o servidor")
    app = DummyApp()
    print("❌ Executando em modo de compatibilidade (sem Flask)")

# ===== CONFIGURAÇÃO DO ASSISTENTE =====
class WebAssistant:
    """Fallback se o core não estiver disponível"""
    def __init__(self):
        self.quick_responses = {
            "saudacao": {
                "message": "Olá! Em que posso ajudar?",
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
            "agradecimento": {
                "message": "Obrigado pelo contato! Fico feliz em ajudar.",
                "category": "inicio"
            }
        }
        self.conversation_history = []
    
    def search_responses(self, keyword):
        matches = {}
        for key, data in self.quick_responses.items():
            if (keyword.lower() in key.lower() or 
                keyword.lower() in data['message'].lower() or
                keyword.lower() in data['category'].lower()):
                matches[key] = data
        return matches
    
    def add_quick_response(self, key, message, category):
        self.quick_responses[key] = {
            "message": message,
            "category": category
        }
        return True
    
    def save_responses(self):
        # Simula salvamento em modo fallback
        return True

class DummyTemplateEngine:
    """Fallback para template engine"""
    def __init__(self):
        self.templates = {
            "encaminhamento": "Estou encaminhando seu caso para o setor {setor}. O protocolo é {protocolo}.",
            "resolucao": "Confirmo que o problema {problema} foi resolvido. Precisa de mais alguma coisa?",
            "atualizacao": "Atualização do caso {caso}: {status}. Previsão: {previsao}."
        }
    
    def list_templates(self):
        return list(self.templates.keys())
    
    def get_template_preview(self, template_name):
        return self.templates.get(template_name, "Template não encontrado")
    
    def fill_template(self, template_name, **kwargs):
        template = self.templates.get(template_name)
        if template:
            try:
                return template.format(**kwargs)
            except KeyError as e:
                return f"Erro: Campo {e} não fornecido"
        return "Template não encontrado"

# Instancia os componentes
if CORE_AVAILABLE:
    try:
        assistant = ChatAssistant(data_dir=os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
        template_engine = TemplateEngine()
        print("✅ Usando módulos core reais")
    except Exception as e:
        print(f"❌ Erro ao instanciar módulos core: {e}")
        assistant = WebAssistant()
        template_engine = DummyTemplateEngine()
        CORE_AVAILABLE = False
else:
    assistant = WebAssistant()
    template_engine = DummyTemplateEngine()
    print("⚠️  Executando em modo fallback (core)")

# ===== ROTAS DA API =====
@app.route('/')
def index():
    """Página principal da interface web"""
    if not FLASK_AVAILABLE:
        return "<h1>Erro: Flask não está instalado</h1><p>Execute: pip install Flask==2.3.3 Flask-CORS==4.0.0</p>"
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Endpoint de saúde da aplicação"""
    return jsonify({
        'status': 'healthy' if FLASK_AVAILABLE else 'degraded',
        'flask_available': FLASK_AVAILABLE,
        'core_available': CORE_AVAILABLE,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/responses')
def get_responses():
    """Retorna todas as respostas rápidas"""
    try:
        return jsonify({
            'success': True,
            'data': assistant.quick_responses,
            'count': len(assistant.quick_responses),
            'mode': 'core' if CORE_AVAILABLE else 'fallback'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search')
def search_responses():
    """Busca respostas por termo"""
    try:
        query = request.args.get('q', '') if FLASK_AVAILABLE else ''
        if query:
            results = assistant.search_responses(query)
            return jsonify({
                'success': True,
                'data': results,
                'count': len(results),
                'query': query
            })
        else:
            return jsonify({
                'success': True,
                'data': assistant.quick_responses,
                'count': len(assistant.quick_responses)
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/copy', methods=['POST'])
def copy_response():
    """Prepara resposta para copiar"""
    try:
        if FLASK_AVAILABLE:
            data = request.get_json()
        else:
            # Fallback para modo sem Flask
            data = {'key': 'saudacao'}
            
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados JSON inválidos'
            }), 400
            
        response_key = data.get('key')
        
        if not response_key:
            return jsonify({
                'success': False,
                'error': 'Chave da resposta não fornecida'
            }), 400
        
        if response_key in assistant.quick_responses:
            message = assistant.quick_responses[response_key]['message']
            
            return jsonify({
                'success': True, 
                'data': {
                    'message': message,
                    'key': response_key,
                    'category': assistant.quick_responses[response_key]['category']
                }
            })
        
        return jsonify({
            'success': False,
            'error': f'Resposta "{response_key}" não encontrada'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/templates')
def get_templates():
    """Retorna templates disponíveis"""
    try:
        templates = template_engine.list_templates()
        templates_data = {}
        for template in templates:
            templates_data[template] = template_engine.get_template_preview(template)
        
        return jsonify({
            'success': True,
            'data': templates_data,
            'count': len(templates_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/response/add', methods=['POST'])
def add_response():
    """Adiciona nova resposta rápida"""
    try:
        if FLASK_AVAILABLE:
            data = request.get_json()
        else:
            return jsonify({
                'success': False,
                'error': 'Funcionalidade não disponível em modo fallback'
            }), 503
            
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados JSON inválidos'
            }), 400
            
        key = data.get('key')
        message = data.get('message')
        category = data.get('category', 'geral')
        
        if not key or not message:
            return jsonify({
                'success': False,
                'error': 'Chave e mensagem são obrigatórias'
            }), 400
        
        if key in assistant.quick_responses:
            return jsonify({
                'success': False,
                'error': f'Já existe uma resposta com a chave "{key}"'
            }), 409
        
        # Adiciona a resposta
        success = assistant.add_quick_response(key, message, category)
        
        if success and CORE_AVAILABLE:
            assistant.save_responses()
        
        return jsonify({
            'success': True,
            'data': {
                'key': key,
                'message': message,
                'category': category
            },
            'message': 'Resposta adicionada com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def main():
    """Função principal para executar o servidor"""
    print("🚀 Assistente VocalCom Web - Inicializando...")
    print(f"📁 Diretório: {os.getcwd()}")
    print(f"🔧 Core disponível: {CORE_AVAILABLE}")
    print(f"🌐 Flask disponível: {FLASK_AVAILABLE}")
    
    if not FLASK_AVAILABLE:
        print("\n❌ ERRO CRÍTICO: Flask não está instalado!")
        print("💡 Para corrigir, execute:")
        print("   pip install Flask==2.3.3 Flask-CORS==4.0.0 Werkzeug==2.3.7")
        print("\n📋 Comandos de instalação:")
        print("   cd web")
        print("   pip install -r requirements.txt")
        return
    
    print(f"\n✅ Servidor pronto!")
    print("📍 Acesse: http://localhost:5000")
    
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5500,
        threaded=True
    )

if __name__ == '__main__':
    main()