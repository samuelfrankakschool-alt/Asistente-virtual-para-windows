import speech_recognition as sr
import pyttsx3
import subprocess
import webbrowser
import pyautogui
import keyboard
import time
import os
import psutil
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
import random
import psutil
import shutil
import requests
from playsound import playsound
from deep_translator import GoogleTranslator
import pygetwindow as gw
import wikipediaapi
from groq import Groq
import pyperclip

#Carga las credenciales
load_dotenv()
ULTIMA_APP = None #Aqui se guarda la memoria del asistente
wikipedia.set_lang('es') #Configurar wikipedia
client_groq = Groq(api_key=os.getenv('GROQ_API_KEY'))
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

# Diccionario de frases
DICCIONARIO_FRASES = {
    "saludo": [
        "¿Qué hubo pues? ¿En qué te ayudo?",
        "Diga, jefe. Soy todo oídos (y código).",
        "¡Epa Joan! ¿Qué se cocina para hoy?",
        "Aquí estoy, listo para el combate. ¿Qué necesitas?",
        "Hola, hola. Espero que el código te compile a la primera hoy."
    ],
    "abriendo_app": [
        "¡Listo! Abriendo eso de una.",
        "Hágale, ahí te lo abro en un segundo.",
        "Procesando... ¡Pum! Ahí lo tienes.",
        "Dale, ya me pongo en esas. No parpadees.",
        "¡Marchando! Espero que no sea para perder el tiempo, ¿no?"
    ],
    "spotify_play": [
        "¡Uff, temazo! Ya suena en Spotify.",
        "Dale, pongámosle ritmo a este día.",
        "Buena elección, Joan. Ya te pongo a sonar.",
        "Listo, ya le subo al volumen para que rinda el trabajo.",
        "Poniendo música... Que no se diga que no tenemos gusto."
    ],
    "noticias_inicio": [
        "Veamos qué se dice en los periódicos hoy...",
        "Buscando los chismes del mundo, dame un momento.",
        "Consultando la prensa. Espero que no todo sea drama.",
        "A ver qué está pasando por ahí afuera...",
        "Abriendo el noticiero express de JP."
    ],
    "ocr_inicio": [
        "Listo, activa el pulso de cirujano y selecciona el área.",
        "Hágale, dime qué parte quieres que lea por ti.",
        "Ojos digitales activados. Selecciona el texto.",
        "A ver, ponme a prueba con esa imagen.",
        "Listo, selecciona lo que te da pereza leer."
    ],
    "ocr_vacio": [
        "Uy, ahí no veo ni un punto. Intenta de nuevo.",
        "Eso está más blanco que una hoja nueva. No hay texto.",
        "No pude leer nada, Joan. Asegúrate de que el texto sea claro.",
        "Mis sensores dicen que ahí no dice nada interesante."
    ],
    "recordatorio_set": [
        "¡Anotado! No se me olvida, te lo juro.",
        "Vale, yo te aviso. Quédate tranquilo.",
        "Entendido, me guardo eso en la memoria para que no se te pase.",
        "¡Listo jefe! Te pego el grito en el tiempo que me dijiste."
    ],
    "despedida": [
        "¡Chao pues! Ahí nos vemos.",
        "Me voy a descansar los circuitos. ¡Hablamos!",
        "Listo, cualquier cosa me pegas el grito por Telegram.",
        "¡Todo bien! Que tengas un resto de día excelente.",
        "Descansa, Joan. No te quedes programando hasta tarde."
    ],
    "error": [
        "¡Epa! Algo se tostó aquí. Intenta de nuevo.",
        "Hubo un error... pero no fue mi culpa, fue de Windows.",
        "Se me cruzaron los cables. No pude hacer eso.",
        "Uy, me diste un comando que no entendí. Repítelo, porfa."
    ],
    "ram_info": [
        "Estás usando el {porcentaje}% de la RAM. ",
        "Pues, tienes ocupado el {porcentaje}% de la memoria. ",
        "La RAM va por el {porcentaje}%. ",
        "En este momento el consumo es del {porcentaje}%. "
    ],
    "ram_comentario": [
        "Vas sobrado, Joan.",
        "Todo normal por ahora.",
        "Ojo que ya se está llenando el tanque.",
        "¡Cuidado! Esa memoria va a explotar si abres otra pestaña de Chrome.",
        "Estamos al límite, deberías cerrar algo."
    ],
    "cpu_info": [
        "El procesador está trabajando al {porcentaje}%.",
        "La CPU va a toda máquina, está al {porcentaje}%.",
        "El uso del cerebro electrónico es del {porcentaje}%.",
        "Actualmente el procesador reporta un {porcentaje}% de carga."
    ],
    "bateria_info": [
        "Tienes el {porcentaje}% de carga y actualmente {estado}.",
        "La batería está al {porcentaje}% y {estado}.",
        "Reporte de energía: {porcentaje}% de batería y el cargador está {estado}."
    ],
    "limpieza_inicio": [
        "Entendido, voy a sacar la basura del sistema. Dame un momento.",
        "Haciendo aseo general... eliminando archivos temporales.",
        "¡Listo! Ya me pongo el overol para limpiar los archivos basura.",
        "Borrando temporales. Tu PC me lo va a agradecer."
    ],
    "limpieza_fin": [
        "¡Limpieza terminada! Logré borrar {archivos} elementos.",
        "Aseo completo. He eliminado {archivos} archivos que no servían.",
        "Listo Joan, PC libre de basura. Borré {archivos} archivos temporales.",
        "Terminé. El sistema está un poco más ligero ahora (borré {archivos} cosas)."
    ],
    "clima_inicio": [
        "Déjame asomarme a la ventana digital...",
        "Consultando el satélite, dame un segundo.",
        "A ver qué dice el reporte meteorológico para hoy.",
        "Revisando el cielo por ti, Joan."
    ],
    "clima_respuesta": [
        "Actualmente en {ciudad} hace {temp}°C con {desc}.",
        "El clima en {ciudad} reporta {temp}°C y el cielo está {desc}.",
        "Te cuento: {temp} grados centígrados y tenemos {desc} en {ciudad}."
    ],
    "hora_info": [
        "Son las {hora}.",
        "En este momento son las {hora}.",
        "Claro, la hora es {hora}.",
        "Mira, son las {hora}. ¡El tiempo vuela!",
        "Reloj checador: son las {hora}."
    ],
    "fecha_info": [
        "Hoy es {fecha}.",
        "Claro Joan, hoy estamos a {fecha}.",
        "Calendario en mano: hoy es {fecha}.",
        "Hoy es {fecha}. ¡No olvides tus entregas!",
        "Dato del día: estamos a {fecha}."
    ],
    "cierre_inicio": [
        "Entendido, voy a liberar RAM cerrando lo más pesado.",
        "Limpiando la casa... cerrando aplicaciones de alto consumo.",
        "Haciendo espacio. Adiós a los procesos pesados.",
        "Voy a darle un respiro a tu procesador. Dame un segundo."
    ],
    "cierre_fin": [
        "Listo. He cerrado {n} aplicaciones pesadas. El sistema debería ir mejor ahora.",
        "Operación terminada. Eliminé {n} procesos que estaban devorando recursos.",
        "Limpieza de procesos completada. ¡Ya tienes más aire en la RAM!",
        "He matado {n} procesos pesados. ¡Dale con toda ahora!"
    ],
    "nota_inicio": [
        "Listo, soy todo oídos. ¿Qué quieres que anote?",
        "Dime y yo lo guardo para que no se te olvide.",
        "Papel y lápiz digital listos. Dispara.",
        "Claro Joan, dictame lo que necesites."
    ],
    "nota_guardada": [
        "Anotado en tu bloc de notas.",
        "Listo, ya lo guardé en el archivo de notas.",
        "Hecho. Ya está guardado para después.",
        "Guardado con éxito. Ya puedes seguir en lo tuyo."
    ],
    "traduccion_inicio": [
        "Claro, esto suena así en inglés:",
        "Traduciendo de una...",
        "Aquí tienes la traducción:",
        "En inglés se dice:"
    ]
}

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

def escucha():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        #Reduce el ruido ambiental rapidamente
        r.adjust_for_ambient_noise(source, duration=0.8)
        hablar('Escuchando...')
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print('Procesando voz...')
            comando = r.recognize_google(audio, language='es-CO')
            print(f'Dijiste {comando}')
            return comando.lower()
        except Exception as e:
            print('No se detecto una voz o hubo un error')
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
        hablar(random.choice(DICCIONARIO_FRASES['ocr_inicio']))

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
               hablar(random.choice(DICCIONARIO_FRASES['ocr_vacio']))
        else:
            hablar('Selección cancelada')

    except Exception as e:
        print(f'Error OCR: {e}')
        hablar(random.choice(DICCIONARIO_FRASES['error']))

def obtener_noticias():
    try:
        hablar(random.choice(DICCIONARIO_FRASES['noticias_inicio']))
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
        hablar(random.choice(DICCIONARIO_FRASES['error']))

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

def limpiar_temporales():
    # Ruta de carpeta temporal
    rutas = [
        os.environ.get('TEMP'), 
    ]

    contador_borrados = 0

    for ruta in rutas:
        if not ruta or not os.path.exists(ruta):
            continue

        try:
            elementos = os.listdir(ruta)
        except PermissionError:
            print(f"No tengo permiso para leer la carpeta: {ruta}")
            continue

        for elemento in elementos:
            ruta_completa = os.path.join(ruta, elemento)
            try:
                if os.path.isfile(ruta_completa) or os.path.islink(ruta_completa):
                    os.unlink(ruta_completa)
                    contador_borrados += 1
                elif os.path.isdir(ruta_completa):
                    shutil.rmtree(ruta_completa)
                    contador_borrados += 1
            except Exception:
                # Si el archivo está en uso o no hay permiso, saltamos al siguiente
                continue
                
    return contador_borrados

def obtener_clima(ciudad='Neiva'): #Puedes poner tu ciudad por defecto
    api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric&lang=es'

    try:
        hablar(random.choice(DICCIONARIO_FRASES['clima_inicio']))
        respuesta = requests.get(url)
        datos = respuesta.json()

        if datos['cod'] == 200:
            temp = round(datos['main']['temp'])
            desc = datos['weather'][0]['description']
            ciudad_nombre = datos['name']

            frase = random.choice(DICCIONARIO_FRASES['clima_respuesta']).format(
                ciudad=ciudad_nombre, temp=temp, desc=desc
            )

            if 'lluvia' in desc or 'llovizna' in desc:
                frase += ' ¡Mejor lleva paraguas que te mojas!'
            elif temp > 30:
                frase += ' Está haciendo un calor bravo, hidrátate bien'

            hablar(frase)
        else:
            hablar('No pude encontrar el clima para esa ciudad')
    except Exception as e:
        print(f'Error clima: {e}')
        hablar(random.choice(DICCIONARIO_FRASES['error']))

def cerrar_procesos_pesados():
    contador = 0
    #Lista de aplicaciones que NO queremos cerrar bajo ninguna circunstancia
    ignorar = ['python.exe', 'explorer.exe', 'asistente_comando_voz.py', 'svchost.exe', 'taskmgr.exe']

    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            #Si consume más del 2% de la RAM y no está en la lista de ignorar
            if proc.info['memory_percent'] > 2.0 and proc.info['name'].lower() not in ignorar:
                print(f'Cerrando {proc.info['name']} (Consumo: {proc.info['memory_percent']:.2f}%)')
                proc.terminate() #Intento de cierre suave
                contador += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return contador

def guardar_nota(texto_nota):
    try:
        ahora = datetime.now()
        fecha_hora = ahora.strftime('%d/%m/%Y %H:%M:%S')

        with open('mis_notas.txt', 'a', encoding='utf-8') as archivo:
            archivo.write(f'[{fecha_hora}] - {texto_nota}\n')
        return True
    except Exception as e:
        print(f'Error guardando nota: {e}')
        return False
    
def consultar_ia_groq(prompt_texto):
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile", # Un modelo potente y gratuito
            messages=[
                {"role": "system", "content": "Eres JP, un asistente de programación conciso y divertido."},
                {"role": "user", "content": prompt_texto}
            ],
            temperature=0.5,
            max_tokens=300
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f'Error en Groq: {e}')
        return 'Lo siento mi conexión con Groq falló'

def ejecutar_comando(comando):
    global ULTIMA_APP #Se usa para recordar el contexto
    if not comando or comando == '':
        return 'continuar'
    
    #Detectar contexto
    ventana_activa = gw.getActiveWindow()
    titulo_ventana = ventana_activa.title.lower() if ventana_activa else ''

    spotify_abierto = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'Spotify.exe':
            spotify_abierto = True
            break

    if any(x in comando for x in ["pon otra", "siguiente canción", "siguiente", "no me gusta"]):
        try:
            sp.next_track()
            hablar('Cambiando de pista, jefe.')
            return 'continuar' # Esto detiene cualquier búsqueda posterior
        except Exception as e:
            print(f"Error saltando canción: {e}")

    if any(nav in titulo_ventana for nav in ['brave', 'chrome', 'edge', 'google chrome']):
        if 'busca esto' in comando or 'buscar esto' in comando:
            hablar('Claro, ¿Qué busco en esta pestaña?')
            termino = escucha()
            if termino:
                #Escribe en la barra de búsqueda de la pestaña actual
                pyautogui.press('esc') #Por si hay algo abierto
                pyautogui.hotkey('ctrl', 'l') #Selecciona la barra de dirección
                time.sleep(0.2)
                pyautogui.write(termino)
                pyautogui.press('enter')
                hablar(f'Buscando {termino} en Brave')
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
                    hablar(f'{random.choice(DICCIONARIO_FRASES["recordatorio_set"])}. Te aviso en {m} minutos')
                    # Esto permite que el recordatorio "espere" sin trabar el programa
                    hilo = threading.Thread(target=temporizador_recordatorio, args=(tarea, m))
                    hilo.start()
                    return 'continuar'
                
            hablar('No me dijiste en cuánto tiempo')
        except Exception as e:
            print(f'Error {e}')
            hablar(random.choice(DICCIONARIO_FRASES['error']))

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
        hablar(random.choice(DICCIONARIO_FRASES['abriendo_app']))
        webbrowser.open('https://www.youtube.com')
        ULTIMA_APP = 'youtube'
        return 'continuar'

    elif any(x in comando for x in ['abrir navegador', 'abre el navegador']):
        hablar(random.choice(DICCIONARIO_FRASES['abriendo_app']))
        webbrowser.open('https://www.google.com')
        ULTIMA_APP = 'google'
        return 'continuar'

    elif any(x in comando for x in ['abrir notas', 'abre mis notas']):
        hablar(random.choice(DICCIONARIO_FRASES['abriendo_app']))
        webbrowser.open('https://site2.q10.com/User/Login')
        return 'continuar'

    elif any(x in comando for x in ['abrir calculadora', 'abre la calculadora']):
        hablar(random.choice(DICCIONARIO_FRASES['abriendo_app']))
        subprocess.Popen('calc.exe')
        return 'continuar'

    elif any(x in comando for x in ['abrir administrador de tareas', 'abre el administrador de tareas']):
        hablar(random.choice(DICCIONARIO_FRASES['abriendo_app']))
        subprocess.Popen('taskmgr.exe')
        return 'continuar'

    elif any(x in comando for x in ['abrir spotify', 'abre spotify']):
        hablar(random.choice(DICCIONARIO_FRASES['abriendo_app']))
        os.system('start spotify')
        return 'continuar'

    elif any(x in comando for x in ['define', 'qué es', 'quién es', 'busca en wikipedia']):
        termino = comando.replace('define', '').replace('qué es', '').replace('quién es', '').replace('busca en wikipedia', '').strip()

        if termino:
            hablar(f'Buscando {termino} en Wikipedia...')
            try:
             #Definimos el idioma y un User-Agent
                wiki_wiki = wikipediaapi.Wikipedia(
                    language='es',
                    user_agent='AsistenteJP' 
                )

                pagina = wiki_wiki.page(termino)

                if pagina.exists():
                    #Obtenemos un resumen para que no hable por horas
                    resumen = pagina.summary[:300] + '...'
                    hablar(f'Según wikipedia: {resumen}')
                else:
                    hablar(f'No encontré nada sobre {termino}. ¿Quieres que lo busque en Google?')
                    ULTIMA_APP = 'google'

                return 'continuar'
            
            except Exception as e:
                print(f'Error Wikipedia: {e}')
                #Si falla la API especial, intentamos el método tradicional pero con manejo de errores
                try:
                    resumen = wikipedia.summary(termino, sentences=2)
                    hablar(f'Esto fue lo que encontre: {resumen}')
                except:
                    hablar('Parece que Wikipedia tiene los servidores caídos o me bloqueó la entrada')

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
    elif any(x in comando for x in ['pon algo', 'pon música de los', 'pon música de las']):
        termino = comando.replace('pon algo', '').replace('pon música de los', '').replace('pon música de las', '').strip()
        hablar(f'Buscando ambiente {termino} en Spotify...')
        try:
            busqueda = sp.search(q=termino, limit=1, type='playlist')
            if busqueda['playlists']['items']:
                playlist = busqueda['playlists']['items'][0]
                sp.start_playback(context_uri=playlist['uri'])
                sp.shuffle(state=True)
                hablar(f'Listo, ya suena la playlist: {playlist['name']}')
            else:
                hablar(f'No encontré una lista para {termino}')
            return 'continuar'
        except Exception as e:
            print(f'Error en Spotify ambiente: {e}')

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
            hablar(random.choice(DICCIONARIO_FRASES['error']))

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
            hablar(random.choice(DICCIONARIO_FRASES['error']))         

    elif any(x in comando for x in ['reproduce', 'pon música de', 'pon']) and 'otra' not in comando:
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
                frase_random = random.choice(DICCIONARIO_FRASES['spotify_play'])
                hablar(f'{frase_random}. Ya suena {nombre_reproduccion}')
            except:
                pass # A veces el dispositivo no soporta ciertas órdenes de estado inmediatamente

        except Exception as e:
            print(f"Error detallado: {e}")
            hablar(random.choice(DICCIONARIO_FRASES['error']))  

    elif any(x in comando for x in ['pausa', 'detén la musica', 'para la musica']):
        try: sp.pause_playback(); hablar('Pausando')
        except: pass

    elif any(x in comando for x in ['siguiente', 'siguiente canción']):
        try: sp.next_track(); hablar('Siguiente canción') 
        except: pass

    elif 'repite esta canción' in comando or 'repite la canción' in comando:
        try:
            sp.repeat(state='track')
            hablar('Listo, esta canción sonará en bucle')
            return 'continuar'
        except: pass

    elif 'volumen al' in comando:
        try:
            #Extrae el numero del comando
            porcentaje = [int(s) for s in comando.split() if s.isdigit()][0]
            if 0 <= porcentaje <= 100:
                sp.volume(porcentaje)
                hablar(f'Volumen ajustado al {porcentaje} por ciento')
            else:
                hablar('El volumen debe estar entre 0 y 100')
            return 'continuar'
        except: pass

    elif any(x in comando for x in ['lee lo seleccionado', 'qué dice aquí', 'lee esta parte']):
        leer_pantalla_seleccionada()
        return 'continuar'

    elif any(x in comando for x in ['noticias', 'dame las noticias', 'qué pasa en el mundo']):
        obtener_noticias()
        return 'continuar'

    #Este es el comando general del estado del sistema
    elif 'reporte de estado' in comando:
        uso_cpu = psutil.cpu_percent(interval=1)
        uso_ram = psutil.virtual_memory().percent
        bateria = psutil.sensors_battery().percent
        hablar(f'Reporte rápido: CPU al {uso_cpu}%, RAM al {uso_ram}% y BATERIA al {bateria}%')
        return 'continuar'

    #Estos son los comandos unitarios para el estado del sistema
    elif any(x in comando for x in ['cuánta ram', 'uso de memoria', 'memoria ram']):
        #Obtenemos la estadística de la RAM
        ram = psutil.virtual_memory()
        porcentaje = ram.percent

        #Elegimos una frase base y le insertamos el número
        frase_base = random.choice(DICCIONARIO_FRASES['ram_info']).format(porcentaje=porcentaje)

        if porcentaje < 40:
            comentario = DICCIONARIO_FRASES['ram_comentario'][0] #Sobrado
        elif porcentaje < 70:
            comentario = DICCIONARIO_FRASES['ram_comentario'][1] #Normal
        elif porcentaje < 85:
            comentario = DICCIONARIO_FRASES['ram_comentario'][2] #Ojo
        else:
            comentario = DICCIONARIO_FRASES['ram_comentario'][3] #Critico

        hablar(frase_base + comentario)
        return 'continuar'

    elif any(x in comando for x in ['uso de cpu', 'procesador', 'cómo va el procesador']):
        #El interval=1 hace que mida el uso durante 1 segundo para ser más preciso
        uso_cpu = psutil.cpu_percent(interval=1)
        frase = random.choice(DICCIONARIO_FRASES['cpu_info']).format(porcentaje=uso_cpu)

        if uso_cpu > 80:
            hablar(frase + ' ¡Está que hecha humo! Deberías calmarte un poco')
        else:
            hablar(frase + ' Todo marcha sobre ruedas')
        return 'continuar'
    
    elif any(x in comando for x in ['batería', 'estado de energía', 'cuánta carga tiene']):
        bateria = psutil.sensors_battery()
        if bateria is not None:
            porcentaje = bateria.percent
            estado = 'conectado a la corriente' if bateria.power_plugged else 'descargándose, mejor busca el cable'

            frase = random.choice(DICCIONARIO_FRASES['bateria_info']).format(
                porcentaje=porcentaje,
                estado=estado
            )
            hablar(frase)
        else:
            hablar('No pude detectar una bateria. ¿Estas seguro de que esto no es un PC de escritorio?')
        return 'continuar'

    elif any(x in comando for x in ['limpia archivos temporales', 'limpiar temporales', 'borrar basura']):
        hablar(random.choice(DICCIONARIO_FRASES['limpieza_inicio']))

        #Ejecuta la limpieza
        borrados = limpiar_temporales()

        frase_final = random.choice(DICCIONARIO_FRASES['limpieza_fin']).format(archivos=borrados)
        hablar(frase_final)
        return 'continuar'
    
    elif any(x in comando for x in ['clima', 'tiempo', 'va a llover', 'temperatura']):
        #Intentamos extraer una ciudad si la mencionas (ej: "clima en Bogotá")
        if 'en' in comando:
            ciudad = comando.split('en')[-1].strip()
            obtener_clima(ciudad)
        else:
            obtener_clima() #Usa la ciudad por defecto
        return 'continuar'
    
    elif any(x in comando for x in ['qué hora es', 'dame la hora', 'la hora por favor']):
        #Obtiene la hora actual del sistema
        ahora = datetime.now()
        #Formatea para que suene natural
        hora_formateada = ahora.strftime('%I:%M: %p')

        frase = random.choice(DICCIONARIO_FRASES['hora_info']).format(hora=hora_formateada)

        hablar(frase)
        return 'continuar'
    
    elif any(x in comando for x in ['qué día es hoy', 'fecha de hoy', 'qué fecha es']):
        ahora = datetime.now()

        dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

        dia_semana = dias[ahora.weekday()]
        dia_mes = ahora.day
        mes = meses[ahora.month - 1]
        anio = ahora.year

        fecha_final = f'{dia_semana}, {dia_mes} de {mes} de {anio}'

        frase = random.choice(DICCIONARIO_FRASES['fecha_info']).format(fecha=fecha_final)
        hablar(frase)
        return 'continuar'
    
    elif any(x in comando for x in ['cierra aplicaciones pesadas', 'cerrar aplicaciones pesadas', 'liberar recursos']):
        hablar(random.choice(DICCIONARIO_FRASES['cierre_inicio']))

        #Ejecutamos la limpieza de procesos
        n_cerrados = cerrar_procesos_pesados()

        if n_cerrados > 0:
            frase = random.choice(DICCIONARIO_FRASES['cierre_fin']).format(n=n_cerrados)
            hablar(frase)
        else:
            hablar('Busqué, pero no encontré ninguna aplicación abusando de tus recursos en este momento')
        return 'continuar'

    elif 'anota esto' in comando or 'anotar esto' in comando:
        separadores = ['anota esto:', 'anota esto', 'anotar esto']
        nota_extraida = ''

        for sep in separadores:
            if sep in comando:
                nota_extraida = comando.split(sep)[-1].strip()
                break
        
        if not nota_extraida:
            hablar(random.choice(DICCIONARIO_FRASES['nota_inicio']))
            nota_extraida = escucha()

        if nota_extraida:
            if guardar_nota(nota_extraida):
                hablar(random.choice(DICCIONARIO_FRASES['nota_guardada']))
            else:
                hablar(random.choice(DICCIONARIO_FRASES['error']))
        else:
            hablar('Al final no me dijiste nada, así que no anoté nada')
        return 'continuar'

    elif 'traduce' in comando:
        #Extraemos lo que el usuario quiere traducir
        texto_a_traducir = comando.replace('traduce', '').replace('a inglés', '').replace('en inglés', '').strip()

        if texto_a_traducir:
            try:
                traducto = GoogleTranslator(source='es', target='en')
                resultado = traducto.translate(texto_a_traducir)
                hablar(random.choice(DICCIONARIO_FRASES['traduccion_inicio']))
                hablar(resultado)
                print(f'Traducción: {resultado}')
            except Exception as e:
                print(f'Error de traducción: {e}')
                hablar(random.choice(DICCIONARIO_FRASES['error']))
        else:
            hablar('No me dijiste qué quieres traducir')
        return 'continuar'

    elif 'visual studio code' in titulo_ventana or 'vsc' in titulo_ventana or 'prueba.py' in titulo_ventana:
        if any(x in comando for x in ['explica', 'optimiza', 'qué hace']):
            accion = "Explica brevemente qué hace" if "explica" in comando else "Optimiza"
            hablar("Analizando con Groq, esto será rápido.")

            try:
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.5)
                codigo_seleccionado = pyperclip.paste()

                if codigo_seleccionado and len(codigo_seleccionado) > 5:
                    prompt = f"{accion} este código Python:\n\n{codigo_seleccionado}"
                    
                    #Llamamos a la nueva función de Groq
                    respuesta_ia = consultar_ia_groq(prompt)
                    respuesta_voz = respuesta_ia.replace('*', '').replace('`', '').strip()
                    
                    print(f"JP (Groq): {respuesta_ia}")
                    hablar(respuesta_voz[:400]) 
                else:
                    hablar("No detecto código. Selecciónalo en VS Code primero.")
                
                return 'continuar'
            except Exception as e:
                print(f"Error: {e}")
                hablar("Tuve un fallo técnico con Groq.")
                return 'continuar'

    #Este es el comando para que se desconecte
    elif any(x in comando for x in ['descansa', 'adiós', 'chao']):
        hablar(random.choice(DICCIONARIO_FRASES['despedida']))
        return 'salir'
    return 'continuar'

#Bucle principal
def iniciar_asistencia():
    print('>>> ASISTENTE ACTIVO <<<')
    print('Instrucciones: Precionar la tecla "ALT" para hablar')

    while True:
        try:
            #El asistente espera a que precione la tecla ALT
            if keyboard.is_pressed('alt'):
                while keyboard.is_pressed('alt'):
                    pass
                try:
                        playsound('activacion.mp3', block=False)
                except Exception as e:
                    print(f'No se pudo reproducir el sonido: {e}')
                hablar(random.choice(DICCIONARIO_FRASES['saludo']))
                pedido = escucha()

                if pedido != '':
                    estado = ejecutar_comando(pedido)
                    if estado == 'salir':
                        break
                else:
                        hablar('No detecte nada')

                print('\nListo. Preciona ALT cuendo me necesites...')
                time.sleep(0.5)
        except Exception as e:
            print(f'Error en el bucle: {e}')
            continue

if __name__ == '__main__':
    #Lanzamos Telegram en un hilo separado para que no bloquee el reconocimiento de voz
    hilo_telegram = threading.Thread(target=iniciar_telegram_bot, daemon=True)
    hilo_telegram.start()

    iniciar_asistencia()
