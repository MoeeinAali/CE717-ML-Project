(function () {
  // Configuration
  const API_BASE_URL = new URL(document.currentScript.src).origin;
  const CHAT_ENDPOINT = `${API_BASE_URL}/chat`;

  // Inject CSS
  const style = document.createElement("style");
  style.innerHTML = `
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');

        :root {
            --primary-gradient: linear-gradient(135deg, #0052cc 0%, #003380 100%);
            --accent-color: #64ffda;
            --glass-bg: rgba(23, 25, 35, 0.85);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #a0aec0;
            --bot-bubble: rgba(255, 255, 255, 0.1);
            --user-bubble: #0052cc;
        }

        #sharif-chat-widget-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 99999;
            font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, sans-serif;
            direction: rtl;
        }

        #sharif-chat-toggle {
            width: 65px;
            height: 65px;
            border-radius: 50%;
            background: var(--primary-gradient);
            color: white;
            border: 2px solid var(--glass-border);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            z-index: 100000;
        }

        #sharif-chat-toggle:hover {
            transform: scale(1.1) rotate(5deg);
            box-shadow: 0 12px 40px rgba(0, 82, 204, 0.4);
        }

        #sharif-chat-window {
            position: absolute;
            bottom: 90px;
            right: 0;
            width: 380px;
            height: 600px;
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            display: none;
            flex-direction: column;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            opacity: 0;
            transform: translateY(20px) scale(0.95);
            transform-origin: bottom right;
        }

        #sharif-chat-window.open {
            display: flex;
            opacity: 1;
            transform: translateY(0) scale(1);
        }

        .chat-header {
            background: rgba(255, 255, 255, 0.03);
            border-bottom: 1px solid var(--glass-border);
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .header-logo {
            width: 45px;
            height: 45px;
            background: white;
            border-radius: 12px;
            padding: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .header-logo img {
            width: 100%;
            height: auto;
        }

        .header-info h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 700;
            color: var(--text-primary);
        }

        .header-info span {
            font-size: 12px;
            color: var(--accent-color);
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .header-info span::before {
            content: '';
            width: 6px;
            height: 6px;
            background: var(--accent-color);
            border-radius: 50%;
            display: block;
        }

        .close-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 24px;
            cursor: pointer;
            margin-right: auto;
            transition: color 0.2s;
        }

        .close-btn:hover {
            color: white;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
            scrollbar-width: thin;
            scrollbar-color: rgba(255,255,255,0.2) transparent;
        }

        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background-color: rgba(255,255,255,0.2);
            border-radius: 3px;
        }
        
        .message-container {
            display: flex;
            gap: 12px;
            align-items: flex-end;
            max-width: 90%;
            animation: fadeIn 0.3s ease;
        }

        .message-container.user {
            align-self: flex-start;
            flex-direction: row;
        }

        .message-container.bot {
            align-self: flex-end;
            flex-direction: row-reverse;
        }

        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            color: white;
            font-size: 18px;
        }

        .avatar.bot {
            background: var(--primary-gradient);
            border: 1px solid var(--glass-border);
        }

        .avatar.user {
            background: #ffaa00; /* Warm color for user */
        }

        .message {
            padding: 12px 18px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.6;
            position: relative;
            word-wrap: break-word;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.bot {
            background: var(--bot-bg);
            border-top-right-radius: 18px;
            border-bottom-left-radius: 4px;
            color: var(--text-primary);
            border: 1px solid var(--glass-border);
        }

        .message.user {
            background: var(--user-bg);
            color: white;
            border-top-left-radius: 18px;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 15px rgba(0, 82, 204, 0.3);
        }

        .chat-input-area {
            padding: 20px;
            border-top: 1px solid var(--glass-border);
            display: flex;
            gap: 12px;
            background: rgba(0, 0, 0, 0.2);
            align-items: center;
        }

        #chat-input {
            flex: 1;
            padding: 14px 20px;
            border: 1px solid var(--glass-border);
            border-radius: 25px;
            outline: none;
            font-size: 14px;
            background: rgba(255, 255, 255, 0.05);
            color: white;
            transition: all 0.3s;
            font-family: inherit;
        }

        #chat-input:focus {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        #chat-input::placeholder {
            color: rgba(255, 255, 255, 0.4);
        }

        #send-btn {
            background: var(--primary-gradient);
            color: white;
            border: none;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        #send-btn svg {
            scale: 2;
        }

        #send-btn:hover {
            transform: scale(1.05);
        }

        #send-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            background: #444;
        }

        .typing-indicator {
            display: flex;
            gap: 5px;
            padding: 12px 16px;
            background: var(--bot-bg);
            border-radius: 18px;
            border-top-right-radius: 4px;
            align-self: flex-start;
            margin-bottom: 15px;
            display: none;
            border: 1px solid var(--glass-border);
            width: fit-content;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: var(--text-secondary);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        .sources {
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .source-link {
            color: var(--accent-color);
            text-decoration: none;
            display: block;
            margin-top: 4px;
            opacity: 0.8;
            transition: opacity 0.2s;
        }

        .source-link:hover {
            opacity: 1;
            text-decoration: underline;
        }

        @media (max-width: 480px) {
            #sharif-chat-window {
                width: calc(100vw - 40px);
                height: calc(100vh - 120px);
                bottom: 100px;
                right: 20px;
            }
        }
    `;
  document.head.appendChild(style);

  // Inject HTML
  const container = document.createElement("div");
  container.id = "sharif-chat-widget-container";
  container.innerHTML = `
        <div id="sharif-chat-window">
            <div class="chat-header">
                <div class="header-logo">
                    <img src="https://micro.ce.sharif.edu/lib/tpl/writr/images/logo.svg" alt="SUT Logo">
                </div>
                <div class="header-info">
                    <h3>دستیار هوشمند شریف</h3>
                    <span>آنلاین و آماده پاسخگویی</span>
                </div>
                <button class="close-btn">&times;</button>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="message-container bot">
                     <div class="avatar bot">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8" y2="16"></line><line x1="16" y1="16" x2="16" y2="16"></line></svg>
                    </div>
                    <div class="message bot">
                        سلام! 👋 <br>
                        من دستیار هوشمند قوانین آموزشی دانشگاه شریف هستم. هر سوالی در مورد آیین‌نامه‌ها داری بپرس.
                    </div>
                </div>
            </div>
            <div class="typing-indicator" id="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            <div class="chat-input-area">
                <input type="text" id="chat-input" placeholder="سوال خود را اینجا بنویسید..." autocomplete="off"/>
                <button id="send-btn">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
            </div>
        </div>
        <button id="sharif-chat-toggle">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        </button>
    `;
  document.body.appendChild(container);

  // Logic
  const toggleBtn = document.getElementById("sharif-chat-toggle");
  const chatWindow = document.getElementById("sharif-chat-window");
  const closeBtn = document.querySelector(".close-btn");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const messagesContainer = document.getElementById("chat-messages");
  const typingIndicator = document.getElementById("typing-indicator");

  let sessionId = localStorage.getItem("sharif_chat_session_id") || null;

  function toggleChat() {
    chatWindow.classList.toggle("open");
    if (chatWindow.classList.contains("open")) {
      input.focus();
    }
  }

  toggleBtn.addEventListener("click", toggleChat);
  closeBtn.addEventListener("click", toggleChat);

  function addMessage(text, type, sources = []) {
    const container = document.createElement("div");
    container.className = `message-container ${type}`;

    // Avatar
    const avatar = document.createElement("div");
    avatar.className = `avatar ${type}`;

    if (type === "bot") {
      avatar.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8" y2="16"></line><line x1="16" y1="16" x2="16" y2="16"></line></svg>`;
    } else {
      avatar.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;
    }

    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${type}`;

    // Simple basic formatting: convert newlines to <br>
    const formattedText = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;")
      .replace(/\n/g, "<br>");

    msgDiv.innerHTML = formattedText;

    if (sources && sources.length > 0) {
      const sourcesDiv = document.createElement("div");
      sourcesDiv.className = "sources";
      sourcesDiv.innerHTML = "<strong>منابع:</strong>";
      sources.forEach((source) => {
        const link = document.createElement("a");
        link.className = "source-link";
        link.href = source.url || "#";
        link.target = "_blank";
        link.textContent = `- ${source.title || "Unknown Source"}`;
        link.title = source.title; // Tooltip
        sourcesDiv.appendChild(link);
      });
      msgDiv.appendChild(sourcesDiv);
    }

    container.appendChild(avatar);
    container.appendChild(msgDiv);

    messagesContainer.appendChild(container);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";
    input.disabled = true;
    sendBtn.disabled = true;
    typingIndicator.style.display = "flex";
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
      const response = await fetch(CHAT_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: text,
          session_id: sessionId,
        }),
      });

      if (!response.ok) throw new Error("Network response was not ok");

      const data = await response.json();

      // Update session ID if new
      if (data.session_id) {
        sessionId = data.session_id;
        localStorage.setItem("sharif_chat_session_id", sessionId);
      }

      addMessage(data.response, "bot", data.sources);
    } catch (error) {
      console.error("Error:", error);
      addMessage("متاسفانه خطایی رخ داد. لطفا دوباره تلاش کنید.", "bot");
    } finally {
      typingIndicator.style.display = "none";
      input.disabled = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });
})();
