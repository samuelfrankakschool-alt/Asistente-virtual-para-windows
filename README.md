# 🎙️ JP: Asistente Virtual Inteligente (Modo Dios)

JP no es solo un asistente... es tu copiloto digital.
Controla tu PC, entiende tu voz, analiza código, lee tu pantalla y ejecuta tareas como si fuera Jarvis 🚀

---

## 🚀 Características Brutales

- 🧠 IA con Groq (Llama 3): entiende, explica y optimiza código
- 👁️ OCR: lee texto directamente desde tu pantalla
- 🎧 Control por voz inteligente
- ⌨️ Modo productividad con tecla ALT
- 🎵 Integración con Spotify (playlists, canciones, etc.)
- 🌦️ Clima en tiempo real
- 🧹 Limpieza y monitoreo del sistema
- 🤖 Control remoto con Telegram
- 📝 Recordatorios y utilidades

---

## 🛠️ Instalación

Ejecuta:

pip install spotipy groq python-dotenv pyautogui pyperclip pyttsx3 SpeechRecognition requests psutil plyer feedparser python-telegram-bot pytesseract pillow deep-translator wikipedia-api

⚠️ IMPORTANTE:
Debes tener instalado Tesseract OCR en tu sistema.

---

## 🔑 Configuración (.env)

Crea un archivo .env con esto:

# Spotify
SPOTIPY_CLIENT_ID=tu_id
SPOTIPY_CLIENT_SECRET=tu_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

# IA
GROQ_API_KEY=tu_api_key

# Telegram
TELEGRAM_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_id

# Clima
OPENWEATHER_API_KEY=tu_api

---

## ▶️ Modos de Uso

Tienes dos formas de invocar a JP:

### 1. Modo Manos Libres
Ejecuta:
python asistente_comando_voz.py

- Siempre escuchando
- Activa con: "Oye JP"
- Ideal cuando no usas teclado

---

### 2. Modo Productividad
Ejecuta:
python asistente.py

- Solo escucha al presionar ALT
- Perfecto para programar

---

## 🧠 Comandos Estrella

Programación:
- "Explica este código"
- "Optimiza esto"

Visión:
- "Lee lo seleccionado"
- "Qué dice aquí"

Sistema:
- "Limpia archivos temporales"
- "Estado del sistema"

Spotify:
- "Reproduce mi playlist gym"
- "Pon música de Bad Bunny"

Utilidades:
- "Traduce hola a inglés"
- "Recuérdame estudiar en 10 minutos"

Información:
- "Cómo está el clima"
- "Dame noticias"

---

## 📌 Requisitos

- Python 3.12+
- Spotify Premium
- Internet

---

## ⚡ Filosofía

JP convierte tu computador en una estación inteligente.
Menos clicks, más control.

---

Desarrollado por Joan 🔥