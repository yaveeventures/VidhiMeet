/**
 * LexE2EE - End-to-End Encryption library using the Web Crypto API.
 * Provides client-side AES-GCM encryption and decryption.
 */
const LexE2EE = (() => {
  // Derive a CryptoKey from bookingId and salt
  async function deriveKey(bookingId, saltHex) {
    const encoder = new TextEncoder();
    const passphrase = bookingId;
    const salt = hexToBytes(saltHex || "00000000000000000000000000000000");
    
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      encoder.encode(passphrase),
      { name: "PBKDF2" },
      false,
      ["deriveBits", "deriveKey"]
    );
    
    return window.crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt: salt,
        iterations: 10000,
        hash: "SHA-256"
      },
      keyMaterial,
      { name: "AES-GCM", length: 256 },
      false,
      ["encrypt", "decrypt"]
    );
  }

  // Encrypt plaintext using AES-GCM
  async function encrypt(plaintext, key) {
    const encoder = new TextEncoder();
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const ciphertext = await window.crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv: iv
      },
      key,
      encoder.encode(plaintext)
    );
    
    return {
      ciphertext: bytesToBase64(new Uint8Array(ciphertext)),
      iv: bytesToBase64(iv)
    };
  }

  // Decrypt ciphertext using AES-GCM
  async function decrypt(ciphertextBase64, ivBase64, key) {
    const decoder = new TextDecoder();
    const ciphertext = base64ToBytes(ciphertextBase64);
    const iv = base64ToBytes(ivBase64);
    
    try {
      const plaintextBytes = await window.crypto.subtle.decrypt(
        {
          name: "AES-GCM",
          iv: iv
        },
        key,
        ciphertext
      );
      return decoder.decode(plaintextBytes);
    } catch (e) {
      console.error("E2EE Decryption failed:", e);
      return "[Decryption Error: Key mismatch or corrupted data]";
    }
  }

  // Helpers
  function hexToBytes(hex) {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < bytes.length; i++) {
      bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
    }
    return bytes;
  }

  function bytesToBase64(bytes) {
    let binary = "";
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }

  function base64ToBytes(base64) {
    const binary = window.atob(base64);
    const len = binary.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }

  return {
    deriveKey,
    encrypt,
    decrypt
  };
})();
