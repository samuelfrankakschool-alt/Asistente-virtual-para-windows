# 🎙️ Asistente Virtual

Asistente de voz desarrollado en Python capaz de ejecutar comandos del sistema, abrir aplicaciones y controlar Spotify mediante su API oficial.

---

## 🚀 Características

- 🎵 Control de Spotify  
  Reproduce artistas o canciones específicas, activa modo aleatorio, pausa y cambia pistas.

- 💻 Comandos del sistema  
  Control de volumen: subir, bajar y silenciar.

- 🌐 Accesos rápidos  
  Abre YouTube, calculadora y navegador automáticamente.

- 🔐 Seguridad  
  Uso de variables de entorno (.env) para proteger credenciales.

---

## 🛠️ Instalación

### 1. Clonar el repositorio
```
git clone https://github.com/samuelfrankakschool-alt/Asistente-virtual-para-windows.git
cd tu-repositorio
```

### 2. Instalar dependencias
```
pip install -r requirements.txt
```

### 3. Configurar Spotify Developer

1. Ir a https://developer.spotify.com/dashboard
2. Crear una aplicación
3. Obtener:
   - Client ID
   - Client Secret
4. Agregar en Redirect URIs:
```
http://127.0.0.1:8888/callback
```

---

## 🔑 Variables de Entorno

Crea un archivo `.env` en la raíz:

```
SPOTIPY_CLIENT_ID='tu_id_aqui'
SPOTIPY_CLIENT_SECRET='tu_secret_aqui'
SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
```

---

## ▶️ Uso

Ejecuta el asistente:

```
python asistente.py
```

🎤 Mantén presionada la tecla ALT para hablar.

---

## 🧠 Ejemplos de Comandos

- "Reproduce música de Bad Bunny"
- "Pausa la música"
- "Siguiente canción"
- "Sube el volumen"
- "Abre YouTube"
- "Abre el navegador"

---

## ⚖️ Requisitos

- Python 3.x
- Cuenta de Spotify Premium

---

## 📌 Notas

- Asegúrate de tener Spotify abierto en tu dispositivo
- La API de Spotify requiere autenticación inicial en el navegador

---

## 📄 Licencia

Este proyecto es de uso personal y educativo.
