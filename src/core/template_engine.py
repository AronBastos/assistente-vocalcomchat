import pyperclip

class TemplateEngine:
    def __init__(self):
        self.templates = {
            "encaminhamento": "Estou encaminhando seu caso para o setor {setor}. O protocolo é {protocolo}.",
            "resolucao": "Confirmo que o problema {problema} foi resolvido. Precisa de mais alguma coisa?",
            "atualizacao": "Atualização do caso {caso}: {status}. Previsão: {previsao}.",
            "aguardando": "Aguardo as informações solicitadas para dar continuidade ao atendimento.",
            "verificacao": "Vou verificar isso e retorno em {tempo} minutos com uma atualização.",
            "contato_futuro": "Vou entrar em contato novamente {periodo} para verificar se está tudo funcionando."
        }
    
    def fill_template(self, template_key, **kwargs):
        """Preenche template com variáveis"""
        if template_key in self.templates:
            template = self.templates[template_key]
            try:
                filled_template = template.format(**kwargs)
                pyperclip.copy(filled_template)
                return filled_template
            except KeyError as e:
                return f"Erro: Variável {e} não fornecida"
        return "Template não encontrado."
    
    def list_templates(self):
        """Lista todos os templates disponíveis"""
        return list(self.templates.keys())
    
    def get_template_preview(self, template_key):
        """Mostra preview do template com placeholders"""
        if template_key in self.templates:
            return self.templates[template_key]
        return None