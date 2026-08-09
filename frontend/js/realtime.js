/**
 * VidhiMeet Real-time Sync & Sound Notifier System
 * Uses Server-Sent Events (SSE) for primary sync, Web Audio API synthesizer for chimes,
 * and WebSockets for real-time live chat.
 */

const SoundNotifier = (() => {
  let audioCtx = null;

  function getAudioContext() {
    if (!audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        audioCtx = new AudioContext();
      }
    }
    if (audioCtx && audioCtx.state === "suspended") {
      audioCtx.resume();
    }
    return audioCtx;
  }

  // Bind first user interaction to unlock browser autoplay restriction
  document.addEventListener("click", () => { getAudioContext(); }, { once: true });
  document.addEventListener("keydown", () => { getAudioContext(); }, { once: true });

  function playChime() {
    try {
      const ctx = getAudioContext();
      if (!ctx) return;

      const now = ctx.currentTime;
      
      // Tone 1: 523.25 Hz (C5)
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.type = "sine";
      osc1.frequency.setValueAtTime(523.25, now);
      gain1.gain.setValueAtTime(0.12, now);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.start(now);
      osc1.stop(now + 0.35);

      // Tone 2: 783.99 Hz (G5)
      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.type = "sine";
      osc2.frequency.setValueAtTime(783.99, now + 0.12);
      gain2.gain.setValueAtTime(0.15, now + 0.12);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.55);
      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2.start(now + 0.12);
      osc2.stop(now + 0.55);
    } catch (e) {
      console.warn("Could not play notification chime:", e);
    }
  }

  return { playChime, getAudioContext };
})();

class SSEClient {
  constructor() {
    this.eventSource = null;
    this.listeners = new Map(); // eventName -> Array of callbacks
    this.reconnectTimer = null;
  }

  connect() {
    const token = sessionStorage.getItem("lex_access_token") || localStorage.getItem("lex_access_token");
    if (!token) return;

    if (this.eventSource) {
      this.eventSource.close();
    }

    const sseUrl = `/api/v1/events/stream?token=${encodeURIComponent(token)}`;
    this.eventSource = new EventSource(sseUrl);

    this.eventSource.onopen = () => {
      console.log("🟢 [SSE] Persistent event stream connected.");
    };

    this.eventSource.onerror = (err) => {
      console.warn("🟡 [SSE] Stream disconnected or re-connecting...", err);
      if (this.eventSource.readyState === EventSource.CLOSED) {
        this.scheduleReconnect();
      }
    };

    // Listen for default and custom SSE events
    const supportedEvents = [
      "connected",
      "BOOKING_CREATED",
      "DRAFT_REQUEST_SUBMITTED",
      "PROPOSAL_ACCEPTED",
      "CHAT_MESSAGE_RECEIVED"
    ];

    supportedEvents.forEach(evtName => {
      this.eventSource.addEventListener(evtName, (e) => {
        try {
          const data = JSON.parse(e.data);
          this.emit(evtName, data);
        } catch (err) {
          console.error(`Error parsing SSE data for ${evtName}:`, err);
        }
      });
    });
  }

  scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      console.log("🔄 [SSE] Attempting reconnect...");
      this.connect();
    }, 5000);
  }

  on(eventName, callback) {
    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, []);
    }
    this.listeners.get(eventName).push(callback);
  }

  emit(eventName, data) {
    const cbs = this.listeners.get(eventName);
    if (cbs) {
      cbs.forEach(cb => {
        try { cb(data); } catch (e) { console.error(`Error in SSE listener ${eventName}:`, e); }
      });
    }
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
  }
}

class WebSocketChatClient {
  constructor(bookingId, onMessageReceived) {
    this.bookingId = bookingId;
    this.onMessageReceived = onMessageReceived;
    this.socket = null;
  }

  connect() {
    const token = sessionStorage.getItem("lex_access_token") || localStorage.getItem("lex_access_token");
    if (!token || !this.bookingId) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/v1/ws/chat/${this.bookingId}?token=${encodeURIComponent(token)}`;

    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log(`💬 [WS Chat] Connected to live chat session for booking ${this.bookingId}`);
    };

    this.socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === "new_message" && this.onMessageReceived) {
          this.onMessageReceived(payload.message);
        }
      } catch (err) {
        console.error("Error parsing WebSocket message:", err);
      }
    };

    this.socket.onerror = (err) => {
      console.warn("⚠️ [WS Chat] WebSocket error:", err);
    };

    this.socket.onclose = () => {
      console.log("💬 [WS Chat] Connection closed.");
    };
  }

  send(content, encrypted = false, iv = null) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ content, encrypted, iv }));
      return true;
    }
    return false;
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

/**
 * Web Crypto E2EE Key Derivation & AES-GCM Payload Encryption Helper
 */
const E2EE = (() => {
  async function deriveKey(bookingId) {
    const encoder = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      encoder.encode(`VidhiMeet-E2EE-${bookingId}`),
      "PBKDF2",
      false,
      ["deriveKey"]
    );
    return window.crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt: encoder.encode(`salt-${bookingId}`),
        iterations: 100000,
        hash: "SHA-256"
      },
      keyMaterial,
      { name: "AES-GCM", length: 256 },
      false,
      ["encrypt", "decrypt"]
    );
  }

  async function encryptMessage(text, bookingId) {
    try {
      const key = await deriveKey(bookingId);
      const encoder = new TextEncoder();
      const iv = window.crypto.getRandomValues(new Uint8Array(12));
      const ciphertext = await window.crypto.subtle.encrypt(
        { name: "AES-GCM", iv },
        key,
        encoder.encode(text)
      );
      return {
        ciphertext: btoa(String.fromCharCode(...new Uint8Array(ciphertext))),
        iv: btoa(String.fromCharCode(...iv)),
        encrypted: true
      };
    } catch (e) {
      console.warn("E2EE encryption fallback to plaintext:", e);
      return { ciphertext: text, iv: null, encrypted: false };
    }
  }

  async function decryptMessage(encryptedObj, bookingId) {
    if (!encryptedObj || !encryptedObj.encrypted || !encryptedObj.iv) {
      return encryptedObj.ciphertext || encryptedObj.content || encryptedObj;
    }
    try {
      const key = await deriveKey(bookingId);
      const iv = Uint8Array.from(atob(encryptedObj.iv), c => c.charCodeAt(0));
      const ciphertext = Uint8Array.from(atob(encryptedObj.ciphertext || encryptedObj.content), c => c.charCodeAt(0));
      const decrypted = await window.crypto.subtle.decrypt(
        { name: "AES-GCM", iv },
        key,
        ciphertext
      );
      return new TextDecoder().decode(decrypted);
    } catch (e) {
      console.warn("E2EE decryption error:", e);
      return "[Decryption Error: Invalid Key]";
    }
  }

  return { deriveKey, encryptMessage, decryptMessage };
})();

window.E2EE = E2EE;
window.SoundNotifier = SoundNotifier;
window.sseClient = new SSEClient();

