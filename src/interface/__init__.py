import os
import sys

# Adiciona o path para importar dos módulos core
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.chat_assistant import ChatAssistant
from core.template_engine import TemplateEngine

class ChatCLI:
    def __init__(self):
        self.assistant = ChatAssistant()
        self.template_engine = TemplateEngine()
    
    def clear_screen(self):
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Mostra cabeçalho"""
        print("=" * 70)
        print("                🤖 ASSISTENTE VOCALCOM")
        print("           Ferramenta de Respostas Rápidas para Chat")
        print("=" * 70)
    
    def show_categories_menu(self):
        """Mostra menu organizado por categorias"""
        categories = {}
        for key, data in self.assistant.quick_responses.items():
            cat = data["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((key, data["message"]))
        
        print("\n" + "📁 CATEGORIAS DE RESPOSTAS:")
        print("-" * 50)
        
        for category, responses in categories.items():
            print(f"\n🎯 {category.upper()}:")
            for key, message in responses:
                preview = message[:65] + "..." if len(message) > 65 else message
                print(f"   [{key:.<20}] {preview}")
    
    def show_commands_help(self):
        """Mostra os comandos disponíveis"""
        print("\n" + "💡 COMANDOS DISPONÍVEIS:")
        print("-" * 40)
        print(" [buscar <termo>]  ... Buscar respostas por palavra-chave")
        print(" [add] ............. Adicionar nova resposta rápida")
        print(" [template] ........ Usar templates dinâmicos")
        print(" [hist] ............ Ver histórico de uso")
        print(" [sair] ............. Fechar o programa")
        print("-" * 40)
    
    def handle_quick_response(self, key):
        """Lida com seleção de resposta rápida"""
        response = self.assistant.get_response(key)
        if response:
            print(f"\n" + "✅" * 5 + " RESPOSTA COPIADA! " + "✅" * 5)
            print(f"📋 Conteúdo: {response}")
            print("\n💡 Dica: Agora é só colar (Ctrl+V) no VocalCom!")
        else:
            print(f"\n❌ Resposta '{key}' não encontrada.")
        input("\n⏎ Pressione Enter para continuar...")
    
    def handle_search(self, search_term):
        """Lida com busca de respostas"""
        print(f"\n🔍 Buscando por: '{search_term}'")
        results = self.assistant.search_responses(search_term)
        
        if results:
            print(f"\n🎯 Encontrei {len(results)} resultado(s):")
            print("-" * 60)
            for key, data in results.items():
                print(f"\n📝 [{key}]")
                print(f"   {data['message']}")
        else:
            print("\n❌ Nenhuma resposta encontrada para esta busca.")
        input("\n⏎ Pressione Enter para continuar...")
    
    def handle_templates(self):
        """Lida com sistema de templates"""
        print("\n" + "📝" * 5 + " TEMPLATES DINÂMICOS " + "📝" * 5)
        
        templates = self.template_engine.list_templates()
        print("\n📂 Templates disponíveis:")
        for i, template_name in enumerate(templates, 1):
            preview = self.template_engine.get_template_preview(template_name)
            print(f"   {i:2d}. {template_name:<15} → {preview}")
        
        try:
            choice = input("\n🎯 Escolha o template (número ou nome): ").strip().lower()
            
            # Mapeia números para nomes de templates
            template_map = {str(i): template for i, template in enumerate(templates, 1)}
            template_map.update({template.lower(): template for template in templates})
            
            if choice in template_map:
                template_name = template_map[choice]
                self.fill_template_dialog(template_name)
            else:
                print("❌ Template não encontrado.")
                input("\n⏎ Pressione Enter para continuar...")
                
        except (ValueError, IndexError):
            print("❌ Escolha inválida.")
            input("\n⏎ Pressione Enter para continuar...")
    
    def fill_template_dialog(self, template_name):
        """Dialogo para preencher um template específico"""
        print(f"\n📋 Preenchendo template: {template_name}")
        print("💬 Preencha os campos abaixo:")
        
        try:
            if template_name == "encaminhamento":
                setor = input("   📂 Setor para encaminhamento: ")
                protocolo = input("   📄 Número do protocolo: ")
                mensagem = self.template_engine.fill_template(
                    "encaminhamento", 
                    setor=setor, 
                    protocolo=protocolo
                )
            
            elif template_name == "resolucao":
                problema = input("   🔧 Problema resolvido: ")
                mensagem = self.template_engine.fill_template("resolucao", problema=problema)
            
            elif template_name == "atualizacao":
                caso = input("   📁 Número do caso: ")
                status = input("   📊 Status atual: ")
                previsao = input("   ⏰ Previsão: ")
                mensagem = self.template_engine.fill_template(
                    "atualizacao", 
                    caso=caso, 
                    status=status, 
                    previsao=previsao
                )
            
            elif template_name == "verificacao":
                tempo = input("   ⏱️  Tempo para retorno (minutos): ")
                mensagem = self.template_engine.fill_template("verificacao", tempo=tempo)
            
            elif template_name == "contato_futuro":
                periodo = input("   📅 Período (ex: 'amanhã', 'na segunda-feira'): ")
                mensagem = self.template_engine.fill_template("contato_futuro", periodo=periodo)
            
            else:
                # Template sem campos específicos
                mensagem = self.template_engine.fill_template(template_name)
            
            if mensagem.startswith("Erro:"):
                print(f"\n❌ {mensagem}")
            else:
                print(f"\n✅" * 5 + " TEMPLATE COPIADO! " + "✅" * 5)
                print(f"📋 Conteúdo: {mensagem}")
                
        except Exception as e:
            print(f"\n❌ Erro ao preencher template: {e}")
        
        input("\n⏎ Pressione Enter para continuar...")
    
    def add_new_response(self):
        """Adiciona nova resposta rápida"""
        print("\n" + "➕" * 5 + " ADICIONAR NOVA RESPOSTA " + "➕" * 5)
        
        print("\n📝 Preencha os dados da nova resposta:")
        key = input("   🔑 Código único (ex: 'problema_email'): ").strip()
        
        if not key:
            print("❌ Código não pode estar vazio.")
            input("\n⏎ Pressione Enter para continuar...")
            return
        
        if key in self.assistant.quick_responses:
            print("❌ Este código já existe. Escolha outro.")
            input("\n⏎ Pressione Enter para continuar...")
            return
        
        category = input("   📂 Categoria (ex: 'email', 'rede', 'acesso'): ").strip()
        message = input("   💬 Mensagem completa: ").strip()
        
        if not message:
            print("❌ Mensagem não pode estar vazia.")
            input("\n⏎ Pressione Enter para continuar...")
            return
        
        self.assistant.add_quick_response(key, message, category)
        input("\n⏎ Pressione Enter para continuar...")
    
    def show_history(self):
        """Mostra histórico recente"""
        print("\n" + "📊" * 5 + " HISTÓRICO RECENTE " + "📊" * 5)
        
        if not self.assistant.conversation_history:
            print("\n📝 Nenhum registro no histórico ainda.")
            print("   As respostas usadas aparecerão aqui.")
        else:
            print(f"\n📈 Últimas {min(5, len(self.assistant.conversation_history))} respostas:")
            print("-" * 70)
            
            for i, entry in enumerate(reversed(self.assistant.conversation_history[-5:]), 1):
                print(f"\n{i}. ⏰ {entry['timestamp']}")
                print(f"   📝 {entry['context']}")
                response_preview = entry['response'][:70] + "..." if len(entry['response']) > 70 else entry['response']
                print(f"   💬 {response_preview}")
        
        input("\n⏎ Pressione Enter para continuar...")
    
    def run(self):
        """Loop principal da aplicação"""
        try:
            while True:
                self.clear_screen()
                self.show_header()
                self.show_categories_menu()
                self.show_commands_help()
                
                user_input = input("\n🎯 Digite o código da resposta ou comando: ").strip()
                
                if user_input.lower() == 'sair':
                    print("\n👋 Obrigado por usar o Assistente VocalCom! Até logo! 👋")
                    break
                
                elif user_input.lower().startswith('buscar '):
                    search_term = user_input[7:].strip()
                    if search_term:
                        self.handle_search(search_term)
                    else:
                        print("❌ Por favor, digite um termo para buscar.")
                        input("\n⏎ Pressione Enter para continuar...")
                
                elif user_input.lower() == 'add':
                    self.add_new_response()
                
                elif user_input.lower() == 'template':
                    self.handle_templates()
                
                elif user_input.lower() == 'hist':
                    self.show_history()
                
                elif user_input in self.assistant.quick_responses:
                    self.handle_quick_response(user_input)
                
                else:
                    print(f"❌ Comando ou código '{user_input}' não reconhecido.")
                    print("💡 Use um dos códigos listados ou comandos disponíveis.")
                    input("\n⏎ Pressione Enter para continuar...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Programa encerrado. Até logo! 👋")
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            input("Pressione Enter para sair...")