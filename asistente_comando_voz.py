import speech_recognition as sr
import pyttsx3
import subprocess
import webbrowser
import pyautogui
import keyboard
import time
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from datetime import datetime, timedelta
import threading
from plyer import notification
import wikipedia
import pytesseract
from PIL import ImageGrab, ImageOps
import tkinter as tk
import feedparser
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv() #Carga las credenciales
wikipedia.set_lang('es') #Configurar wikipedia
WAKE_WORD = "oye jp" #Palabra clave para activar la asistente
ULTIMA_APP = None #Aqui se guarda la memoria del asistente
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#Configuración de la API de Spotify
scope = 'user-modify-playback-state user-read-playback-state playlist-read-private'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope=scope,
    cache_path='.cache'
))

def hablar(texto):
    print(f'Asistente: {texto}')
    #Se reinicia el motor para evitar que se bloquee
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    #Se aplica la configuración de una voz en español
    for voz in voices:
        if 'spanish' in voz.name.lower() or 'mexico' in voz.name.lower() or 'spain' in voz.name.lower():
            engine.setProperty('voice', voz.id)
            break

    engine.setProperty('rate', 185)
    engine.say(texto)
    engine.runAndWait()
    engine.stop()

def escucha_comando_real():
    #Escucha el comando después de la actividad
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print('Esperando orden...')
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            comando = r.recognize_google(audio, language='es-CO')
            print(f'Orden recibida: {comando}')
            return comando.lower()
        except:
            return ''
        
def temporizador_recordatorio(tarea, minutos):
    #Esta función corre en un hilo separado para no bloquear al asistente
    segundos = minutos * 60
    time.sleep(segundos)

    #Esto lanza la notificación visual y sonora de windows
    notification.notify(
        title = 'Recordatorio de JP',
        message = f'Es hora de: {tarea}',
        app_name = 'JP Asistente',
        timeout = 10
    )
    #Hacemos que hable cuando el tiempo se acabe/cumpla
    hablar(f'Ya llego el momento de {tarea}')

class AreaSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3) #Hace una ventana trasparente
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.config(cursor='cross')

        self.canvas = tk.Canvas(self.root, cursor='cross', bg='grey')
        self.canvas.pack(fill='both', expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.coords = None

        self.canvas.bind('<ButtonPress-1>', self.on_button_press)
        self.canvas.bind('<B1-Motion>', self.on_move_press)
        self.canvas.bind('<ButtonRelease-1>', self.on_button_release)
        self.root.bind('<Escape>', lambda e: self.root.destroy())

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x , end_y = (event.x, event.y)
        self.coords = (min(self.start_x, end_x), min(self.start_y, end_y),
                       max(self.start_x, end_x), max(self.start_y, end_y))
        self.root.destroy()

def leer_pantalla_seleccionada():
    try:
        hablar('Selecciona con el ratón el área que quieres que lea')

        #Abrimos el selector
        selector = AreaSelector()
        selector.root.mainloop()

        if selector.coords:
            #Captura solo el área selecionada
            captura = ImageGrab.grab(bbox=selector.coords)
            captura = ImageOps.grayscale(captura)
            texto_extraido = pytesseract.image_to_string(captura, lang='spa')

            if texto_extraido.strip():
                print(f'Texto detectado: {texto_extraido}')
                hablar('Dice lo siguiente:')
                hablar(texto_extraido)
            else:
                hablar('No encontré texto claro en esa selección')
        else:
            hablar('Selección cancelada')

    except Exception as e:
        print(f'Error OCR: {e}')
        hablar('Tuve un problema al procesar la imagen')

def obtener_noticias():
    try:
        hablar('Buscando las noticias más recientes del momento...')
        #URL del RSS de Google News en español
        url_noticias = 'https://news.google.com/rss?hl=es-419&gl=CO&ceid=CO:es-419'

        feed = feedparser.parse(url_noticias)
        #Se toma las primeras 3 noticias para no saturar
        noticias = feed.entries[:3]

        if noticias:
            hablar('Estas son las tres noticias principales:')
            for i, entrada in enumerate(noticias):
                titular = entrada.title.split(' - ')[0]
                print(f'Noticia {i+1}: {titular}')
                hablar(f'Noticia {i+1}: {titular}')
                time.sleep(0.5)
            hablar('Este es el resumen por ahora')
        else:
            hablar('Lo siento, no puedo conectarme con el servidor de noticias')

    except Exception as e:
        print(f'Error Noticias: {e}')
        hablar('Hubo un error al intentar leer las noticias')

async def manejar_mensaje_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Solo respondera a tu id de usuario
    mi_id = os.getenv('TELEGRAM_CHAT_ID')
    if str(update.effective_user.id) != str(mi_id):
        await update.message.reply_text('Acceso denegado. No eres mi dueño')
        return
    
    texto_recibido = update.message.text.lower()
    print(f'Mensaje de Telegram: {texto_recibido}')

    resultado = ejecutar_comando(texto_recibido)

    if resultado == 'salir':
        await update.message.reply_text('Entendido, cerrando JP en la PC')
    else: 
        await update.message.reply_text(f'Comando "{texto_recibido}" ejecutando en tu PC')

def iniciar_telegram_bot():
    token = os.getenv('TELEGRAM_TOKEN')
    app = ApplicationBuilder().token(token).build()

    # Maneja cualquier mensaje de texto
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), manejar_mensaje_telegram))

    print('>>> BOT DE TELEGRAM ACTIVO <<<')
    app.run_polling()

def ejecutar_comando(comando):
    global ULTIMA_APP #Se usa para recordar el contexto
    if not comando:
        return 'continuar'
    
    #Esta es la lógica de recordatorios
    if 'recuerdame' in comando or 'recuérdame' in comando:
        try:
            #Extraer la tarea y el tiempo
            parte_tarea = comando.replace('recuerdame', '').replace('recuérdame', '')
            
            if 'en' in parte_tarea:
                partes = parte_tarea.split('en')
                tarea = partes[0].strip()
                tiempo_texto = partes[1].strip()

                #Se limpia números
                minutos = [int(s) for s in tiempo_texto.split() if s.isdigit()]

                if minutos:
                    m = minutos[0]
                    hablar(f'Entiendo. Te avisare sobre {tarea} en {m} minutos')
                    # Esto permite que el recordatorio "espere" sin trabar el programa
                    hilo = threading.Thread(target=temporizador_recordatorio, args=(tarea, m))
                    hilo.start()
                    return 'continuar'
                
            hablar('No me dijiste en cuánto tiempo')
        except Exception as e:
            print(f'Error {e}')
            hablar('No pude entender el tiempo del recordatorio')

    #Estos son los comandos de energia
    elif 'apagar el computador' in comando or 'apagar pc' in comando:
        hablar('Apagando el equipo. Hasta luego')
        os.system('shutdown /s /t 1')

    elif 'reinicia el computador' in comando or 'reiniciar pc' in comando:
        hablar('Reiniciando el equipo')
        os.system('shutdown /r /t 1')

    elif 'suspende el computador' in comando or 'suspender pc' in comando:
        hablar('Suspendiendo el equipo')
        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')

    #Estos son los comandos de aplicaciones
    if any(x in comando for x in ['abrir youtube', 'abre youtube']):
        hablar('Abriendo Youtube')
        webbrowser.open('https://www.youtube.com')
        ULTIMA_APP = 'youtube'
        return 'continuar'

    elif any(x in comando for x in ['abrir navegador', 'abre el navegador']):
        hablar('Abriendo Navegador')
        webbrowser.open('https://www.google.com')
        ULTIMA_APP = 'google'
        return 'continuar'

    elif any(x in comando for x in ['abrir notas', 'abre mis notas']):
        hablar('Abriendo Notas')
        webbrowser.open('https://site2.q10.com/User/Login')
        return 'continuar'

    elif any(x in comando for x in ['abrir calculadora', 'abre la calculadora']):
        hablar('Abriendo Calculadora')
        subprocess.Popen('calc.exe')
        return 'continuar'

    elif any(x in comando for x in ['abrir administrador de tareas', 'abre el administrador de tareas']):
        hablar('Abriendo el Administrador de Tareas')
        subprocess.Popen('taskmgr.exe')
        return 'continuar'

    elif any(x in comando for x in ['abrir spotify', 'abre spotify']):
        hablar('Abriendo Spotify')
        os.system('start spotify')
        return 'continuar'

    elif any(x in comando for x in ['define', 'qué es', 'quién es', 'busca en wikipedia']):
        termino = comando.replace('define', '').replace('qué es', '').replace('quién es', '').replace('busca en wikipedia', '').strip()

        if termino:
            hablar(f'Buscando {termino} en Wikipedia...')
            try:
                #Obtiene solo las dos primeras oraciones para que no hable demasiado
                resumen = wikipedia.summary(termino, sentences=2)
                hablar(f'Según Wikipedia: {resumen}')
                return 'continuar'
            except wikipedia.exceptions.DisambiguationError as e:
                hablar(f'Hay varias coincidencias para {termino}. Sé más específico, por ejemplo: {e.options[:3]}')
            except wikipedia.exceptions.PageError:
                hablar(f'No encontré información sobre {termino} en Wikipedia, ¿Quieres que lo busque en Google?')
            except Exception as e:
                print(f'Error Wikipendia: {e}')
                hablar('Tuve un error para conectarme con Wikipedia')
        return 'continuar'

    #Logica de busqueda con contexto
    #Definimos activadores naturales
    disparadores_busqueda = ['busca', 'buscame', 'investiga', 'averigua', 'googlea', 'qué es', 'quién es']
    #Comprueba si alguna de las frases está en el comando
    if any(frase in comando for frase in disparadores_busqueda):
        termino = comando
        #Se limpia el término eliminando el disparador que se haya usado
        for frase in disparadores_busqueda:
            termino = termino.replace(frase, '')
        #Limpieza de conectores innecesarios
        termino = termino.replace('sobre', '').replace('videos de', '').strip()
        #Decición de plataforma
        if 'en youtube' in termino:
            target = 'youtube'
            termino = termino.replace('en youtube', '').strip()
        elif 'en google' in termino:
            target = 'google'
            termino = termino.replace('en google', '').strip()
        else:
            #Si no se especifico, usamos la memoria. Si no hay memoria, Google por defecto
            target = ULTIMA_APP if ULTIMA_APP else 'google'

        if termino:
            if target == 'youtube':
                hablar(f'Buscando {termino} en YouTube')
                webbrowser.open(f'https://www.youtube.com/results?search_query={termino}')
            elif target == 'google':
                hablar(f'Investigando {termino} en Google')
                webbrowser.open(f'https://www.google.com/search?q={termino}')
            else:
                hablar(f'Investigando {termino} en Google')
                webbrowser.open(f'https://www.google.com/search?q={termino}')
            return 'continuar'
            
    #Estos son los comandos del sistema
    elif any(x in comando for x in ['subir volumen', 'sube el volumen']):
        hablar('Subiendo el volumen')
        for _ in range(5):
            pyautogui.press('volumeup')

    elif any(x in comando for x in ['bajar volumen', 'baja el volumen']):
        hablar('Bajando el volumen')
        for _ in range(5):
            pyautogui.press('volumedown')

    elif any(x in comando for x in ['silencio', 'silencia']):
        pyautogui.press('volumemute')
        hablar('Volumen silenciado')

    #Logica de Spotify
    #Lógica de canciones específicas en playlists específicas
    elif 'de mi playlist' in comando or 'en mi playlist' in comando:
        #Esto separa el comando para obtener canción y playlist
        #Ejemplo: Reproduce la vaca lola de mi playlist favorita
        try:
           #limpia el comando de ruidos
            comando_limpio = comando.replace(',', '').replace('.', '')
            #Detecta que conector usaste para separar bien
            separador = 'de mi playlist' if 'de mi playlist' in comando_limpio else 'en mi playlist'
            partes = comando_limpio.split(separador)
            
            #Limpiamos palabras comunes que el usuario dice pero no son parte del nombre
            parte_cancion = partes[0].replace('reproduce', '').replace('pon', '').replace('la canción', '').replace('el tema', '').strip()
            parte_playlist = partes[1].strip()
            
            hablar(f'Buscando {parte_cancion} en tu playlist {parte_playlist}')

            #Busqueda de playlist
            playlist_id = None
            nombre_playlist_real = ''
            results = sp.current_user_playlists(limit=50)

            while results:
                for item in results['items']:
                    #Buscamos si el nombre que dijiste está contenido en el nombre real
                    if parte_playlist.lower() in item['name'].lower():
                        playlist_id = item['id']
                        nombre_playlist_real = item['name']
                        break
                if playlist_id or not results['next']: break
                results = sp.next(results)

            if playlist_id:
                #Busqueda de la canción dentro de la playlist
                cancion_encontrada = None
                results_tracks = sp.playlist_items(playlist_id)

                #Definimos una lista de "ruido" para limpiar la búsqueda de la canción si falla
                palabras_ruido = ['la', 'el', 'un', 'una', 'de', 'del']

                while results_tracks:
                    for item in results_tracks['items']:
                        #Verificamos que el item no sea nulo (por si hay anuncios o podcasts)
                        track = item.get('track')
                        if track and 'name' in track:
                            nombre_track = track['name'].lower()
                            p_cancion_low = parte_cancion.lower()
                            
                            #Intento 1: Match directo o contenido
                            if p_cancion_low in nombre_track or nombre_track in p_cancion_low:
                                cancion_encontrada = track
                                break
                            
                            #Intento 2: Limpieza de artículos (por si dijiste "la bachata" y se llama "Bachata")
                            p_limpia = " ".join([w for w in p_cancion_low.split() if w not in palabras_ruido])
                            if p_limpia in nombre_track and len(p_limpia) > 2:
                                cancion_encontrada = track
                                break
                                
                    if cancion_encontrada or not results_tracks['next']: break
                    results_tracks = sp.next(results_tracks)

                if cancion_encontrada:
                    sp.start_playback(uris=[cancion_encontrada['uri']])
                    #Usamos comillas dobles externas para que las simples internas de los comentarios no rompan el string
                    hablar(f"Poniendo {cancion_encontrada['name']} de tu playlist {nombre_playlist_real}")
                else:
                    hablar(f'No encontré "{parte_cancion}" dentro de tu playlist {nombre_playlist_real}')
            else:
                hablar(f'No encontré ninguna playlist que se llame {parte_playlist}')
        except Exception as e:
            print(f'Error: {e}')
            hablar('No pude procesar la búsqueda en tu playlist')

    elif 'reproduce mi playlist' in comando:
        nombre_playlist = comando.replace('reproduce mi playlist', '').strip()
        hablar(f'Buscando tu playlist {nombre_playlist} en spotify')

        try:
            #Esto obtiene las playlist
            playlist = sp.current_user_playlists()
            playlist_id = None

            for item in playlist['items']:
                if nombre_playlist.lower() in item['name'].lower():
                    playlist_id = item['id']
                    nombre_real = item['name']
                    break

            if playlist_id:
                sp.start_playback(context_uri=f'spotify:playlist:{playlist_id}')
                time.sleep(1.5)
                sp.shuffle(state=True)
                hablar(f'Listo. ya suena tu playlist {nombre_real} en modo aleatorio')
            else:
                hablar(f'No encontré ninguna playlist llamada {nombre_playlist} en tu biblioteca')
        except Exception as e:
            print(f'Error en Playlists: {e}')
            hablar('No puede acceder a tus playlist')     

    elif any(x in comando for x in ['reproduce', 'pon música de', 'pon']):
        termino = comando.replace('reproduce', '').replace('pon música de', '').replace('pon', '').strip()
        hablar(f'Buscando {termino} en Spotify')

        try:
            # Buscamos con un límite un poco mayor para comparar mejor
            busqueda_track = sp.search(q=termino, limit=2, type='track')
            busqueda_artist = sp.search(q=termino, limit=1, type='artist')

            track = busqueda_track['tracks']['items'][0] if busqueda_track['tracks']['items'] else None
            artist = busqueda_artist['artists']['items'][0] if busqueda_artist['artists']['items'] else None

            # ESTRATEGIA: Si la canción existe y el término está en el título, ponemos la canción.
            # Solo ponemos el artista si el nombre coincide perfectamente.
            
            if artist and artist['name'].lower() == termino.lower():
                # Caso Artista Exacto
                sp.start_playback(context_uri=artist['uri'])
                nombre_reproduccion = f'éxitos de {artist["name"]}'
            
            elif track:
                # Caso Canción (Prioridad si no es artista exacto)
                # Usamos la URI de la canción
                sp.start_playback(uris=[track['uri']])
                nombre_reproduccion = f'{track["name"]} de {track["artists"][0]["name"]}'
            
            elif artist:
                # Caso Artista por relevancia (fallback)
                sp.start_playback(context_uri=artist['uri'])
                nombre_reproduccion = f'música de {artist["name"]}'
            else:
                hablar('No encontré esa canción ni el artista')
                return 'continuar'

            # CONFIGURACIÓN DE REPRODUCCIÓN AUTOMÁTICA Y SHUFFLE
            time.sleep(1.5) 
            try:
                # Quitamos el bucle (repetir) para que al terminar pase a la radio/siguiente
                sp.repeat(state='off') 
                # Activamos el modo aleatorio
                sp.shuffle(state=True)
                hablar(f'Listo Joan, ya suena {nombre_reproduccion}')
            except:
                pass # A veces el dispositivo no soporta ciertas órdenes de estado inmediatamente

        except Exception as e:
            print(f"Error detallado: {e}")
            hablar('Asegúrate de tener Spotify abierto en este dispositivo') 

    elif any(x in comando for x in ['pausa', 'detén la musica', 'para la musica']):
        try: sp.pause_playback(); hablar('Pausando')
        except: pass

    elif any(x in comando for x in ['siguiente', 'siguiente canción']):
        try: sp.next_track(); hablar('Siguiente canción') 
        except: pass

    elif any(x in comando for x in ['lee lo seleccionado', 'qué dice aquí', 'lee esta parte']):
        leer_pantalla_seleccionada()
        return 'continuar'

    elif any(x in comando for x in ['noticias', 'dame las noticias', 'qué pasa en el mundo']):
        obtener_noticias()
        return 'continuar'

    #Este es el comando para que se desconecte
    elif any(x in comando for x in ['descansa', 'adiós', 'chao']):
        hablar('Hasta luego, que tengas un resto de buen día')
        return 'salir'
    return 'continuar'

def iniciar_asistente():
    r = sr.Recognizer()
    r.energy_threshold = 300 #Ajustamos la sensibilidad para que no sea tan estricto con el ruido
    print(f'>>> ASISTENTE ESCUCHANDO: Di {WAKE_WORD.upper()} <<<')

    while True:
        with sr.Microphone() as source:
            try:
                #Esto hace que escuche costantemente de fondo por fragmentos cortos
                audio = r.listen(source, phrase_time_limit=3)
                texto = r.recognize_google(audio, language='es-CO').lower()

                if WAKE_WORD in texto:
                    print(f'Palabra clave detectada: {texto}')
                    hablar('¿Que necesitas?')
                    #Esto llama la función para escuchar la orden real
                    pedido = escucha_comando_real()
                    if pedido:
                        if ejecutar_comando(pedido) == 'salir':
                            break
                    print(f'\nEsperando "{WAKE_WORD}"...')
            except sr.UnknownValueError:
                #Si no se detecta voz clara, seguira escuchando
                continue
            except Exception as e:
                continue

if __name__ == '__main__':
    #Lanzamos Telegram en un hilo separado para que no bloquee el reconocimiento de voz
    hilo_telegram = threading.Thread(target=iniciar_telegram_bot, daemon=True)
    hilo_telegram.start()
    
    iniciar_asistente()

