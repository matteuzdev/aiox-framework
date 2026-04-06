/**
 * Konig SDR Widget - Chat flutuante para sites.
 * Inspirado no widget do GPT Maker.
 * 
 * Uso: <script src="https://seu-servidor.com/api/widget.js"></script>
 */
(function() {
    'use strict';

    // Evita duplicacao
    if (window.__konigWidgetLoaded) return;
    window.__konigWidgetLoaded = true;

    // Config padrao
    var CONFIG = {
        apiBase: 'http://localhost:8000',
        title: 'Konig SDR',
        subtitle: 'Assistente de Vendas',
        greeting: 'Ola! Sou o assistente virtual da Konig Systems. Como posso te ajudar hoje?',
        placeholder: 'Digite sua mensagem...',
        primaryColor: '#6366f1',
        position: 'right',
        companyName: 'Konig Systems',
        botAvatar: '🤖',
        userAvatar: '👤',
    };

    // Sessao unica por visitante
    var sessionId = sessionStorage.getItem('konig_session_id') || generateId();
    sessionStorage.setItem('konig_session_id', sessionId);

    // Estado
    var isOpen = false;
    var messages = [];
    var isTyping = false;
    var userName = '';
    var userEmail = '';
    var askingForEmail = false;

    function generateId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
    }

    // Carrega config do servidor
    function loadConfig() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', CONFIG.apiBase + '/api/widget-config', true);
        xhr.onload = function() {
            if (xhr.status === 200) {
                var cfg = JSON.parse(xhr.responseText);
                for (var key in cfg) {
                    if (cfg.hasOwnProperty(key)) {
                        CONFIG[key] = cfg[key];
                    }
                }
            }
        };
        xhr.send();
    }
    loadConfig();

    // Cria elementos do widget
    function createWidget() {
        // Container principal
        var container = document.createElement('div');
        container.id = 'konig-widget-container';
        container.style.cssText = 'position:fixed;z-index:999999;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;';

        // Botao flutuante
        var button = document.createElement('div');
        button.id = 'konig-widget-button';
        button.style.cssText = 'position:fixed;bottom:24px;' + (CONFIG.position === 'left' ? 'left:24px' : 'right:24px') + ';width:60px;height:60px;border-radius:50%;background:' + CONFIG.primaryColor + ';color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.15);transition:all 0.3s ease;z-index:999999;';
        button.innerHTML = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>';
        button.onmouseenter = function() { this.style.transform = 'scale(1.1)'; };
        button.onmouseleave = function() { this.style.transform = 'scale(1)'; };
        button.onclick = toggleChat;

        // Painel de chat
        var chatPanel = document.createElement('div');
        chatPanel.id = 'konig-chat-panel';
        chatPanel.style.cssText = 'position:fixed;bottom:100px;' + (CONFIG.position === 'left' ? 'left:24px' : 'right:24px') + ';width:380px;max-width:calc(100vw - 48px);height:520px;max-height:calc(100vh - 140px);background:#fff;border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,0.12);display:none;flex-direction:column;overflow:hidden;z-index:999998;';

        // Header
        var header = document.createElement('div');
        header.style.cssText = 'background:' + CONFIG.primaryColor + ';color:#fff;padding:16px 20px;display:flex;align-items:center;justify-content:space-between;';
        header.innerHTML = '<div><div style="font-weight:600;font-size:16px;">' + CONFIG.title + '</div><div style="font-size:12px;opacity:0.9;">' + CONFIG.subtitle + '</div></div><button id="konig-close-btn" style="background:none;border:none;color:#fff;cursor:pointer;font-size:20px;padding:4px 8px;border-radius:4px;">&times;</button>';
        header.querySelector('#konig-close-btn').onclick = toggleChat;

        // Area de mensagens
        var messagesArea = document.createElement('div');
        messagesArea.id = 'konig-messages';
        messagesArea.style.cssText = 'flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;background:#f8f9fa;';

        // Input area
        var inputArea = document.createElement('div');
        inputArea.style.cssText = 'padding:12px 16px;background:#fff;border-top:1px solid #e5e7eb;display:flex;gap:8px;align-items:center;';

        var input = document.createElement('input');
        input.id = 'konig-input';
        input.type = 'text';
        input.placeholder = CONFIG.placeholder;
        input.style.cssText = 'flex:1;border:1px solid #e5e7eb;border-radius:8px;padding:10px 14px;font-size:14px;outline:none;';
        input.onkeydown = function(e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

        var sendBtn = document.createElement('button');
        sendBtn.id = 'konig-send-btn';
        sendBtn.style.cssText = 'background:' + CONFIG.primaryColor + ';color:#fff;border:none;border-radius:8px;padding:10px 16px;cursor:pointer;font-size:14px;font-weight:500;transition:opacity 0.2s;';
        sendBtn.innerHTML = 'Enviar';
        sendBtn.onmouseenter = function() { this.style.opacity = '0.85'; };
        sendBtn.onmouseleave = function() { this.style.opacity = '1'; };
        sendBtn.onclick = sendMessage;

        inputArea.appendChild(input);
        inputArea.appendChild(sendBtn);
        chatPanel.appendChild(header);
        chatPanel.appendChild(messagesArea);
        chatPanel.appendChild(inputArea);
        container.appendChild(button);
        container.appendChild(chatPanel);
        document.body.appendChild(container);

        // Mensagem de boas-vindas
        addMessage(CONFIG.greeting, 'bot');
    }

    function toggleChat() {
        var panel = document.getElementById('konig-chat-panel');
        var button = document.getElementById('konig-widget-button');
        isOpen = !isOpen;
        panel.style.display = isOpen ? 'flex' : 'none';
        button.style.display = isOpen ? 'none' : 'flex';
        if (isOpen) {
            document.getElementById('konig-input').focus();
        }
    }

    function addMessage(text, type) {
        var area = document.getElementById('konig-messages');
        var msg = document.createElement('div');
        msg.style.cssText = 'max-width:80%;padding:10px 14px;border-radius:12px;font-size:14px;line-height:1.5;word-wrap:break-word;';

        if (type === 'bot') {
            msg.style.cssText += 'background:#fff;color:#1f2937;align-self:flex-start;border-bottom-left-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,0.05);';
            msg.innerHTML = '<div style="font-size:12px;color:#6b7280;margin-bottom:4px;">' + CONFIG.botAvatar + ' ' + CONFIG.title + '</div>' + formatText(text);
        } else {
            msg.style.cssText += 'background:' + CONFIG.primaryColor + ';color:#fff;align-self:flex-end;border-bottom-right-radius:4px;';
            msg.textContent = text;
        }

        area.appendChild(msg);
        area.scrollTop = area.scrollHeight;
    }

    function addTypingIndicator() {
        var area = document.getElementById('konig-messages');
        var typing = document.createElement('div');
        typing.id = 'konig-typing';
        typing.style.cssText = 'align-self:flex-start;background:#fff;padding:10px 14px;border-radius:12px;border-bottom-left-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,0.05);';
        typing.innerHTML = '<div style="display:flex;gap:4px;"><span style="width:8px;height:8px;background:#9ca3af;border-radius:50%;animation:konig-bounce 1.4s infinite;"></span><span style="width:8px;height:8px;background:#9ca3af;border-radius:50%;animation:konig-bounce 1.4s infinite 0.2s;"></span><span style="width:8px;height:8px;background:#9ca3af;border-radius:50%;animation:konig-bounce 1.4s infinite 0.4s;"></span></div>';
        area.appendChild(typing);
        area.scrollTop = area.scrollHeight;

        // Adiciona animacao CSS
        if (!document.getElementById('konig-bounce-style')) {
            var style = document.createElement('style');
            style.id = 'konig-bounce-style';
            style.textContent = '@keyframes konig-bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-8px)}}';
            document.head.appendChild(style);
        }
    }

    function removeTypingIndicator() {
        var typing = document.getElementById('konig-typing');
        if (typing) typing.remove();
    }

    function formatText(text) {
        // Formata basico: negrito, quebras de linha
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
    }

    function sendMessage() {
        var input = document.getElementById('konig-input');
        var text = input.value.trim();
        if (!text || isTyping) return;

        input.value = '';
        addMessage(text, 'user');
        isTyping = true;
        addTypingIndicator();

        // Detecta se usuario deu nome/email
        var nameMatch = text.match(/meu nome [\u00e9e]?\s*(.+)/i) || text.match(/sou\s+(.+)/i);
        var emailMatch = text.match(/[\w.-]+@[\w.-]+\.\w+/);

        if (nameMatch && !userName) {
            userName = nameMatch[1].trim();
        }
        if (emailMatch && !userEmail) {
            userEmail = emailMatch[0];
        }

        // Envia para o backend
        var xhr = new XMLHttpRequest();
        xhr.open('POST', CONFIG.apiBase + '/api/chat', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            removeTypingIndicator();
            isTyping = false;
            if (xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                addMessage(data.reply, 'bot');
            } else {
                addMessage('Desculpe, ocorreu um erro. Pode tentar novamente?', 'bot');
            }
        };
        xhr.onerror = function() {
            removeTypingIndicator();
            isTyping = false;
            addMessage('Desculpe, estou com dificuldade de conectar. Pode me deixar seu email que entro em contato?', 'bot');
        };

        var payload = JSON.stringify({
            session_id: sessionId,
            message: text,
            user_name: userName || null,
            user_email: userEmail || null,
            source_url: window.location.href,
        });
        xhr.send(payload);
    }

    // Inicializa
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createWidget);
    } else {
        createWidget();
    }
})();
