/**
 * Garrido Sportech — Chat Widget Embebible
 * 
 * Uso en cualquier sitio:
 *   <script src="https://TU-SERVIDOR/widget/chat-widget.js" 
 *           data-api="https://TU-SERVIDOR" defer></script>
 * 
 * Para desarrollo local:
 *   <script src="http://localhost:8000/widget/chat-widget.js" 
 *           data-api="http://localhost:8000" defer></script>
 */
(function () {
  "use strict";

  // ── Configuración ───────────────────────────────────────────────────
  // Buscar el script tag antes de que se pierda la referencia
  const allScripts = document.querySelectorAll('script[data-api]');
  const scriptTag = allScripts.length > 0 ? allScripts[allScripts.length - 1] : null;
  const API_URL = (scriptTag && scriptTag.getAttribute("data-api")) || "http://localhost:8000";

  let sessionId = null;
  let isOpen = false;
  let isLoading = false;

  // ── Estilos ─────────────────────────────────────────────────────────
  const styles = document.createElement("style");
  styles.textContent = `
    #gs-chat-widget * {
      box-sizing: border-box !important;
      margin: 0 !important;
      padding: 0 !important;
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    #gs-chat-btn {
      position: fixed !important;
      bottom: 100px !important;
      right: 24px !important;
      width: 64px !important;
      height: 64px !important;
      border-radius: 50% !important;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
      border: none !important;
      cursor: pointer !important;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
      z-index: 999999 !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }

    #gs-chat-btn:hover {
      transform: scale(1.1);
      box-shadow: 0 6px 28px rgba(0,0,0,0.4);
    }

    #gs-chat-btn svg {
      width: 30px;
      height: 30px;
      fill: #ffffff;
      transition: transform 0.3s ease;
    }

    #gs-chat-btn.open svg.chat-icon { display: none; }
    #gs-chat-btn.open svg.close-icon { display: block; }
    #gs-chat-btn:not(.open) svg.chat-icon { display: block; }
    #gs-chat-btn:not(.open) svg.close-icon { display: none; }

    #gs-chat-btn .pulse {
      position: absolute;
      width: 64px;
      height: 64px;
      border-radius: 50%;
      background: rgba(26, 26, 46, 0.3);
      animation: gs-pulse 2s ease-out infinite;
    }

    @keyframes gs-pulse {
      0% { transform: scale(1); opacity: 0.6; }
      100% { transform: scale(1.8); opacity: 0; }
    }

    #gs-chat-window {
      position: fixed !important;
      bottom: 176px !important;
      right: 24px !important;
      width: 400px;
      max-width: calc(100vw - 32px);
      height: 560px;
      max-height: calc(100vh - 140px);
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 12px 48px rgba(0,0,0,0.2);
      z-index: 999998 !important;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      opacity: 0;
      transform: translateY(20px) scale(0.95);
      pointer-events: none;
      transition: opacity 0.3s ease, transform 0.3s ease;
    }

    #gs-chat-window.visible {
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: all;
    }

    /* Header */
    .gs-header {
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: white;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }

    .gs-header-logo {
      width: 40px;
      height: 40px;
      background: rgba(255,255,255,0.15);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }

    .gs-header-info h3 {
      font-size: 15px;
      font-weight: 600;
      margin-bottom: 2px;
    }

    .gs-header-info span {
      font-size: 12px;
      opacity: 0.8;
    }

    .gs-header-actions {
      margin-left: auto;
      display: flex;
      gap: 8px;
    }

    .gs-header-actions button {
      background: rgba(255,255,255,0.15);
      border: none;
      color: white;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s;
    }

    .gs-header-actions button:hover {
      background: rgba(255,255,255,0.25);
    }

    /* Mensajes */
    .gs-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: #f8f9fa;
    }

    .gs-messages::-webkit-scrollbar {
      width: 4px;
    }

    .gs-messages::-webkit-scrollbar-thumb {
      background: #ccc;
      border-radius: 4px;
    }

    .gs-msg {
      max-width: 85%;
      padding: 10px 14px;
      border-radius: 14px;
      font-size: 14px;
      line-height: 1.5;
      word-wrap: break-word;
    }

    .gs-msg.user {
      align-self: flex-end;
      background: #1a1a2e;
      color: white;
      border-bottom-right-radius: 4px;
    }

    .gs-msg.bot {
      align-self: flex-start;
      background: white;
      color: #333;
      border: 1px solid #e8e8e8;
      border-bottom-left-radius: 4px;
    }

    .gs-msg.bot a {
      color: #1a73e8;
      text-decoration: none;
    }

    .gs-msg.bot a:hover {
      text-decoration: underline;
    }

    .gs-msg.welcome {
      align-self: center;
      background: transparent;
      border: none;
      color: #666;
      font-size: 13px;
      text-align: center;
      max-width: 100%;
      padding: 8px;
    }

    /* Quick actions */
    .gs-quick-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 0 16px 12px;
      background: #f8f9fa;
    }

    .gs-quick-btn {
      background: white;
      border: 1px solid #ddd;
      border-radius: 20px;
      padding: 6px 14px;
      font-size: 12px;
      color: #555;
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;
    }

    .gs-quick-btn:hover {
      background: #1a1a2e;
      color: white;
      border-color: #1a1a2e;
    }

    /* Typing indicator */
    .gs-typing {
      display: flex;
      gap: 4px;
      padding: 12px 16px;
      align-self: flex-start;
    }

    .gs-typing span {
      width: 8px;
      height: 8px;
      background: #ccc;
      border-radius: 50%;
      animation: gs-bounce 1.4s ease-in-out infinite;
    }

    .gs-typing span:nth-child(2) { animation-delay: 0.2s; }
    .gs-typing span:nth-child(3) { animation-delay: 0.4s; }

    @keyframes gs-bounce {
      0%, 80%, 100% { transform: translateY(0); }
      40% { transform: translateY(-8px); }
    }

    /* Input */
    .gs-input-area {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      gap: 8px;
      border-top: 1px solid #eee;
      background: white;
      flex-shrink: 0;
    }

    .gs-input-area input {
      flex: 1;
      border: 1px solid #e0e0e0;
      border-radius: 24px;
      padding: 10px 16px;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }

    .gs-input-area input:focus {
      border-color: #1a1a2e;
    }

    .gs-input-area input:disabled {
      background: #f5f5f5;
    }

    .gs-send-btn {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #1a1a2e;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s, transform 0.1s;
      flex-shrink: 0;
    }

    .gs-send-btn:hover { background: #16213e; }
    .gs-send-btn:active { transform: scale(0.95); }
    .gs-send-btn:disabled { background: #ccc; cursor: not-allowed; }

    .gs-send-btn svg {
      width: 18px;
      height: 18px;
      fill: white;
    }

    /* Footer */
    .gs-footer {
      text-align: center;
      padding: 8px;
      font-size: 11px;
      color: #aaa;
      background: white;
      border-top: 1px solid #f0f0f0;
      flex-shrink: 0;
    }

    .gs-footer a {
      color: #888;
      text-decoration: none;
    }

    .gs-footer a:hover {
      color: #1a1a2e;
    }

    /* Mobile */
    @media (max-width: 480px) {
      #gs-chat-window {
        bottom: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        max-height: 100vh !important;
        border-radius: 0 !important;
      }

      #gs-chat-btn {
        bottom: 90px !important;
        right: 16px !important;
        width: 56px !important;
        height: 56px !important;
      }

      #gs-chat-btn .pulse {
        width: 56px !important;
        height: 56px !important;
      }
    }
  `;
  document.head.appendChild(styles);

  // ── HTML ────────────────────────────────────────────────────────────
  const widget = document.createElement("div");
  widget.id = "gs-chat-widget";
  widget.innerHTML = `
    <!-- Botón flotante -->
    <button id="gs-chat-btn" aria-label="Abrir chat Garrido Sportech">
      <div class="pulse"></div>
      <svg class="chat-icon" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/><path d="M7 9h2v2H7zm4 0h2v2h-2zm4 0h2v2h-2z"/></svg>
      <svg class="close-icon" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
    </button>

    <!-- Ventana de chat -->
    <div id="gs-chat-window">
      <div class="gs-header">
        <div class="gs-header-logo">🏋️</div>
        <div class="gs-header-info">
          <h3>Garrido Sportech</h3>
          <span>Asistente Técnico IA</span>
        </div>
        <div class="gs-header-actions">
          <button onclick="gsChat.reset()" title="Nueva conversación">🔄</button>
        </div>
      </div>

      <div class="gs-messages" id="gs-messages">
        <div class="gs-msg welcome">
          👋 ¡Hola! Soy el asistente técnico de <strong>Garrido Sportech</strong>.<br>
          Consulta sobre nuestros sistemas de medición biomecánica.
        </div>
      </div>

      <div class="gs-quick-actions" id="gs-quick-actions">
        <button class="gs-quick-btn" onclick="gsChat.send('¿Qué sistemas tienen disponibles?')">📦 Sistemas</button>
        <button class="gs-quick-btn" onclick="gsChat.send('Cotízame el G-FORCE Alpha')">💰 Cotizar</button>
        <button class="gs-quick-btn" onclick="gsChat.send('¿Tienen validación científica?')">📄 Papers</button>
        <button class="gs-quick-btn" onclick="gsChat.send('¿Dónde descargo el software?')">💻 Software</button>
        <button class="gs-quick-btn" onclick="gsChat.send('¿Cómo los contacto?')">📞 Contacto</button>
      </div>

      <div class="gs-input-area">
        <input type="text" id="gs-input" placeholder="Escribe tu consulta..." 
               onkeydown="if(event.key==='Enter')gsChat.sendInput()" autocomplete="off" />
        <button class="gs-send-btn" onclick="gsChat.sendInput()" id="gs-send-btn" aria-label="Enviar">
          <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
      </div>

      <div class="gs-footer">
        <a href="https://garridosportech.cl" target="_blank">garridosportech.cl</a> · Tecnología aplicada al rendimiento humano
      </div>
    </div>
  `;
  document.body.appendChild(widget);

  // ── Lógica ──────────────────────────────────────────────────────────
  const chatBtn = document.getElementById("gs-chat-btn");
  const chatWindow = document.getElementById("gs-chat-window");
  const messagesEl = document.getElementById("gs-messages");
  const inputEl = document.getElementById("gs-input");
  const sendBtn = document.getElementById("gs-send-btn");
  const quickActions = document.getElementById("gs-quick-actions");

  chatBtn.addEventListener("click", () => {
    isOpen = !isOpen;
    chatBtn.classList.toggle("open", isOpen);
    chatWindow.classList.toggle("visible", isOpen);
    if (isOpen) {
      setTimeout(() => inputEl.focus(), 300);
    }
  });

  function addMessage(text, type) {
    const msg = document.createElement("div");
    msg.className = `gs-msg ${type}`;

    if (type === "bot") {
      // Convertir markdown básico a HTML
      let html = text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
        .replace(/\n/g, "<br>");
      msg.innerHTML = html;
    } else {
      msg.textContent = text;
    }

    messagesEl.appendChild(msg);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showTyping() {
    const typing = document.createElement("div");
    typing.className = "gs-typing";
    typing.id = "gs-typing";
    typing.innerHTML = "<span></span><span></span><span></span>";
    messagesEl.appendChild(typing);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function hideTyping() {
    const el = document.getElementById("gs-typing");
    if (el) el.remove();
  }

  function setLoading(loading) {
    isLoading = loading;
    inputEl.disabled = loading;
    sendBtn.disabled = loading;
    if (loading) showTyping();
    else hideTyping();
  }

  async function sendMessage(text) {
    if (!text.trim() || isLoading) return;

    // Ocultar quick actions después del primer mensaje
    if (quickActions) quickActions.style.display = "none";

    addMessage(text, "user");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}`);
      }

      const data = await response.json();
      sessionId = data.session_id;
      addMessage(data.reply, "bot");
    } catch (err) {
      addMessage("⚠️ No se pudo conectar con el asistente. Intenta de nuevo o contáctanos por WhatsApp.", "bot");
      console.error("Garrido Sportech Chat Error:", err);
    } finally {
      setLoading(false);
    }
  }

  function sendInput() {
    const text = inputEl.value.trim();
    if (text) {
      inputEl.value = "";
      sendMessage(text);
    }
  }

  function reset() {
    if (sessionId) {
      fetch(`${API_URL}/reset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      }).catch(() => {});
    }
    sessionId = null;
    messagesEl.innerHTML = `
      <div class="gs-msg welcome">
        👋 ¡Hola! Soy el asistente técnico de <strong>Garrido Sportech</strong>.<br>
        Consulta sobre nuestros sistemas de medición biomecánica.
      </div>`;
    if (quickActions) quickActions.style.display = "flex";
  }

  // API pública
  window.gsChat = { send: sendMessage, sendInput, reset };

})();
