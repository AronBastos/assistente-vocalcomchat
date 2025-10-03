// Estado da aplicação
class AppState {
    constructor() {
        this.responses = {};
        this.filteredResponses = {};
        this.templates = {};
        this.selectedResponse = null;
        this.searchTerm = '';
    }
}

const appState = new AppState();

// Elementos DOM
const elements = {
    searchInput: document.getElementById('searchInput'),
    clearSearch: document.getElementById('clearSearch'),
    categoriesContainer: document.getElementById('categoriesContainer'),
    previewPlaceholder: document.getElementById('previewPlaceholder'),
    previewActive: document.getElementById('previewActive'),
    previewTitle: document.getElementById('previewTitle'),
    previewCategory: document.getElementById('previewCategory'),
    previewText: document.getElementById('previewText'),
    copyBtn: document.getElementById('copyBtn'),
    useTemplateBtn: document.getElementById('useTemplateBtn'),
    templatesContainer: document.getElementById('templatesContainer'),
    refreshBtn: document.getElementById('refreshBtn'),
    resultsCount: document.getElementById('resultsCount'),
    responseCount: document.getElementById('responseCount'),
    lastUpdate: document.getElementById('lastUpdate'),
    statusIndicator: document.getElementById('statusIndicator'),
    templateModal: document.getElementById('templateModal'),
    modalTitle: document.getElementById('modalTitle'),
    modalBody: document.getElementById('modalBody'),
    closeModal: document.getElementById('closeModal'),
    notification: document.getElementById('notification'),
    notificationText: document.getElementById('notificationText')
};

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    showLoading('Carregando respostas...');
    
    try {
        // Verifica saúde da API
        await checkAPIHealth();
        
        // Carrega dados iniciais
        await Promise.all([
            loadResponses(),
            loadTemplates()
        ]);
        
        updateLastUpdate();
        setupEventListeners();
        
    } catch (error) {
        showError('Erro ao carregar aplicação: ' + error.message);
    }
}

// Verifica saúde da API
async function checkAPIHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateStatusIndicator(true, data.core_available);
        } else {
            updateStatusIndicator(false, false);
        }
    } catch (error) {
        updateStatusIndicator(false, false);
        console.warn('API health check failed:', error);
    }
}

// Atualiza indicador de status
function updateStatusIndicator(connected, coreAvailable) {
    const indicator = elements.statusIndicator;
    const icon = indicator.querySelector('i');
    const text = indicator.querySelector('span');
    
    if (connected) {
        indicator.style.background = '#dcfce7';
        indicator.style.color = '#166534';
        icon.className = 'fas fa-circle';
        icon.style.color = '#22c55e';
        text.textContent = coreAvailable ? 'Conectado' : 'Modo Demo';
    } else {
        indicator.style.background = '#fef2f2';
        indicator.style.color = '#991b1b';
        icon.className = 'fas fa-circle';
        icon.style.color = '#ef4444';
        text.textContent = 'Desconectado';
    }
}

// Carrega todas as respostas
async function loadResponses() {
    try {
        const response = await fetch('/api/responses');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        appState.responses = data;
        appState.filteredResponses = { ...data };
        
        renderResponses();
        updateResponseCount();
        
    } catch (error) {
        console.error('Error loading responses:', error);
        showError('Erro ao carregar respostas: ' + error.message);
        // Usa dados de fallback
        appState.responses = getFallbackResponses();
        appState.filteredResponses = { ...appState.responses };
        renderResponses();
        updateResponseCount();
    }
}

// Dados de fallback
function getFallbackResponses() {
    return {
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
        }
    };
}

// Renderiza as respostas organizadas por categoria
function renderResponses() {
    const responses = appState.filteredResponses;
    
    if (Object.keys(responses).length === 0) {
        elements.categoriesContainer.innerHTML = `
            <div class="loading">
                <i class="fas fa-search"></i>
                Nenhuma resposta encontrada para "${appState.searchTerm}"
            </div>
        `;
        return;
    }
    
    // Agrupa por categoria
    const categories = {};
    Object.entries(responses).forEach(([key, data]) => {
        const category = data.category || 'geral';
        if (!categories[category]) {
            categories[category] = [];
        }
        categories[category].push({ key, ...data });
    });
    
    // Ordena categorias
    const sortedCategories = Object.keys(categories).sort();
    
    let html = '';
    
    sortedCategories.forEach(category => {
        const categoryResponses = categories[category];
        
        html += `
            <div class="category">
                <div class="category-header">
                    <span>${category.toUpperCase()}</span>
                    <span class="category-count">${categoryResponses.length}</span>
                </div>
                <div class="responses-list">
        `;
        
        categoryResponses.forEach(response => {
            const isActive = appState.selectedResponse === response.key ? 'active' : '';
            const messagePreview = response.message.length > 100 
                ? response.message.substring(0, 100) + '...' 
                : response.message;
                
            html += `
                <div class="response-item ${isActive}" 
                     onclick="selectResponse('${response.key}')"
                     data-key="${response.key}">
                    <div class="response-code">${response.key}</div>
                    <div class="response-message">${messagePreview}</div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    elements.categoriesContainer.innerHTML = html;
    updateResultsCount();
}

// Atualiza contador de resultados
function updateResultsCount() {
    const count = Object.keys(appState.filteredResponses).length;
    const total = Object.keys(appState.responses).length;
    
    if (appState.searchTerm) {
        elements.resultsCount.textContent = `${count} de ${total} respostas encontradas para "${appState.searchTerm}"`;
    } else {
        elements.resultsCount.textContent = `${count} respostas disponíveis`;
    }
}

// Atualiza contador total de respostas
function updateResponseCount() {
    const count = Object.keys(appState.responses).length;
    elements.responseCount.textContent = `${count} respostas carregadas`;
}

// Atualiza timestamp da última atualização
function updateLastUpdate() {
    const now = new Date();
    elements.lastUpdate.textContent = `Última atualização: ${now.toLocaleTimeString('pt-BR')}`;
}

// Seleciona uma resposta
function selectResponse(responseKey) {
    // Remove seleção anterior
    document.querySelectorAll('.response-item.active').forEach(item => {
        item.classList.remove('active');
    });
    
    // Adiciona seleção atual
    const selectedItem = document.querySelector(`[data-key="${responseKey}"]`);
    if (selectedItem) {
        selectedItem.classList.add('active');
    }
    
    const response = appState.responses[responseKey];
    if (!response) return;
    
    appState.selectedResponse = responseKey;
    
    // Atualiza preview
    elements.previewPlaceholder.style.display = 'none';
    elements.previewActive.style.display = 'block';
    
    elements.previewTitle.textContent = responseKey;
    elements.previewCategory.textContent = response.category;
    elements.previewText.textContent = response.message;
    
    // Mostra/oculta botão de template
    if (response.message.includes('{')) {
        elements.useTemplateBtn.style.display = 'block';
    } else {
        elements.useTemplateBtn.style.display = 'none';
    }
}

// Configura event listeners
function setupEventListeners() {
    // Busca em tempo real
    elements.searchInput.addEventListener('input', debounce(function(e) {
        appState.searchTerm = e.target.value.trim();
        searchResponses(appState.searchTerm);
    }, 300));
    
    // Limpar busca
    elements.clearSearch.addEventListener('click', function() {
        elements.searchInput.value = '';
        appState.searchTerm = '';
        searchResponses('');
    });
    
    // Copiar resposta
    elements.copyBtn.addEventListener('click', copySelectedResponse);
    
    // Usar como template
    elements.useTemplateBtn.addEventListener('click', function() {
        if (appState.selectedResponse) {
            openTemplateModal(appState.selectedResponse);
        }
    });
    
    // Atualizar
    elements.refreshBtn.addEventListener('click', function() {
        loadResponses();
        loadTemplates();
        updateLastUpdate();
        showNotification('Dados atualizados!');
    });
    
    // Fechar modal
    elements.closeModal.addEventListener('click', closeModal);
    
    // Fechar modal clicando fora
    elements.templateModal.addEventListener('click', function(e) {
        if (e.target === elements.templateModal) {
            closeModal();
        }
    });
    
    // Tecla ESC para fechar modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

// Busca respostas
async function searchResponses(query) {
    if (!query) {
        appState.filteredResponses = { ...appState.responses };
        renderResponses();
        return;
    }
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        appState.filteredResponses = data;
        renderResponses();
        
    } catch (error) {
        console.error('Search error:', error);
        // Fallback: busca local
        const filtered = {};
        Object.entries(appState.responses).forEach(([key, data]) => {
            if (key.toLowerCase().includes(query.toLowerCase()) ||
                data.message.toLowerCase().includes(query.toLowerCase()) ||
                data.category.toLowerCase().includes(query.toLowerCase())) {
                filtered[key] = data;
            }
        });
        appState.filteredResponses = filtered;
        renderResponses();
    }
}

// Copia resposta selecionada
async function copySelectedResponse() {
    if (!appState.selectedResponse) {
        showNotification('Selecione uma resposta primeiro!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/copy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                key: appState.selectedResponse
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Tenta copiar usando Clipboard API moderna
            try {
                await navigator.clipboard.writeText(data.text);
                showNotification('✅ Resposta copiada para a área de transferência!');
            } catch (clipboardError) {
                // Fallback para navegadores antigos
                const textArea = document.createElement('textarea');
                textArea.value = data.text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                showNotification('✅ Resposta copiada! (método alternativo)');
            }
        } else {
            showNotification('❌ Erro: ' + data.error, 'error');
        }
        
    } catch (error) {
        console.error('Copy error:', error);
        showNotification('❌ Erro ao copiar resposta', 'error');
    }
}

// Carrega templates
async function loadTemplates() {
    try {
        const response = await fetch('/api/templates');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        appState.templates = data;
        renderTemplates();
        
    } catch (error) {
        console.error('Error loading templates:', error);
        appState.templates = getFallbackTemplates();
        renderTemplates();
    }
}

// Templates de fallback
function getFallbackTemplates() {
    return {
        "encaminhamento": "Estou encaminhando seu caso para o setor {setor}. O protocolo é {protocolo}.",
        "resolucao": "Confirmo que o problema {problema} foi resolvido. Precisa de mais alguma coisa?",
        "atualizacao": "Atualização do caso {caso}: {status}. Previsão: {previsao}."
    };
}

// Renderiza templates
function renderTemplates() {
    const templates = appState.templates;
    
    if (Object.keys(templates).length === 0) {
        elements.templatesContainer.innerHTML = `
            <div class="loading">
                <i class="fas fa-info-circle"></i>
                Nenhum template disponível
            </div>
        `;
        return;
    }
    
    let html = '';
    
    Object.entries(templates).forEach(([name, preview]) => {
        html += `
            <div class="template-item" onclick="openTemplateModal('${name}')">
                <div class="template-name">${name}</div>
                <div class="template-preview">${preview}</div>
            </div>
        `;
    });
    
    elements.templatesContainer.innerHTML = html;
}

// Abre modal de template
function openTemplateModal(templateNameOrKey) {
    const isResponseTemplate = appState.responses[templateNameOrKey];
    const templateName = isResponseTemplate ? 'Resposta Personalizada' : templateNameOrKey;
    const templatePreview = isResponseTemplate 
        ? appState.responses[templateNameOrKey].message
        : appState.templates[templateNameOrKey];
    
    elements.modalTitle.textContent = `Preencher Template: ${templateName}`;
    
    // Extrai campos do template
    const fields = extractTemplateFields(templatePreview);
    
    let formHtml = `
        <div class="form-info">
            <p><strong>Template:</strong> ${templatePreview}</p>
        </div>
        <div class="form-fields">
    `;
    
    fields.forEach(field => {
        formHtml += `
            <div class="form-group">
                <label for="field-${field}">${field.replace('_', ' ').toUpperCase()}:</label>
                <input type="text" id="field-${field}" placeholder="Digite o valor para ${field}...">
            </div>
        `;
    });
    
    formHtml += `
        </div>
        <div class="form-actions">
            <button onclick="generateTemplate('${templateNameOrKey}', ${isResponseTemplate})" 
                    class="btn-primary" style="width: 100%;">
                <i class="fas fa-magic"></i> Gerar e Copiar
            </button>
        </div>
    `;
    
    elements.modalBody.innerHTML = formHtml;
    elements.templateModal.style.display = 'block';
}

// Extrai campos de um template
function extractTemplateFields(template) {
    const fieldRegex = /{(\w+)}/g;
    const fields = [];
    let match;
    
    while ((match = fieldRegex.exec(template)) !== null) {
        if (!fields.includes(match[1])) {
            fields.push(match[1]);
        }
    }
    
    return fields;
}

// Fecha modal
function closeModal() {
    elements.templateModal.style.display = 'none';
    elements.modalBody.innerHTML = '';
}

// Gera template preenchido
async function generateTemplate(templateName, isResponse = false) {
    const fields = extractTemplateFields(
        isResponse 
            ? appState.responses[templateName].message 
            : appState.templates[templateName]
    );
    
    const fieldValues = {};
    let allFilled = true;
    
    fields.forEach(field => {
        const input = document.getElementById(`field-${field}`);
        const value = input.value.trim();
        
        if (value) {
            fieldValues[field] = value;
        } else {
            allFilled = false;
            input.style.borderColor = '#ef4444';
        }
    });
    
    if (!allFilled) {
        showNotification('❌ Preencha todos os campos!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/template/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                template_name: templateName,
                fields: fieldValues,
                is_response: isResponse
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Copia para clipboard
            try {
                await navigator.clipboard.writeText(data.text);
                showNotification('✅ Template gerado e copiado!');
                closeModal();
                
                // Atualiza preview com o resultado
                elements.previewText.textContent = data.text;
                
            } catch (clipboardError) {
                const textArea = document.createElement('textarea');
                textArea.value = data.text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                showNotification('✅ Template gerado! (copiado com método alternativo)');
                closeModal();
            }
        } else {
            showNotification('❌ Erro: ' + data.error, 'error');
        }
        
    } catch (error) {
        console.error('Template generation error:', error);
        showNotification('❌ Erro ao gerar template', 'error');
    }
}

// Utilitários
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showNotification(message, type = 'success') {
    elements.notificationText.textContent = message;
    
    if (type === 'error') {
        elements.notification.style.background = '#ef4444';
    } else {
        elements.notification.style.background = '#10b981';
    }
    
    elements.notification.classList.add('show');
    
    setTimeout(() => {
        elements.notification.classList.remove('show');
    }, 3000);
}

function showLoading(message) {
    elements.categoriesContainer.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            ${message}
        </div>
    `;
}

function showError(message) {
    elements.categoriesContainer.innerHTML = `
        <div class="loading">
            <i class="fas fa-exclamation-triangle"></i>
            ${message}
        </div>
    `;
    console.error(message);
}