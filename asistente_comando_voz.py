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

#Carga las credenciales
load_dotenv()

#Palabra clave para activar la asistente
WAKE_WORD = "oye jp"

#Configuración de la API de Spotify
scope = 'user-modify-playback-state user-read-playback-state'
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
        
def ejecutar_comando(comando):
    if not comando:
        return 'continuar'
    
    #Estos son los comandos de aplicaciones
    if 'abrir youtube' in comando:
        hablar('Abriendo Youtube')
        webbrowser.open('https://www.youtube.com')

    elif 'abrir navegador' in comando:
        hablar('Abriendo Navegador')
        webbrowser.open('https://www.google.com')

    elif 'abrir notas' in comando:
        hablar('Abriendo Notas')
        webbrowser.open('https://site2.q10.com/User/Login')

    elif 'abrir calculadora' in comando:
        hablar('Abriendo Calculadora')
        subprocess.Popen('calc.exe')

    elif 'abrir spotify' in comando:
        hablar('Abriendo Spotify')
        os.system('start spotify')

    #Estos son los comandos del sistema
    elif 'subir volumen' in comando:
        hablar('Subiendo el volumen')
        for _ in range(5):
            pyautogui.press('volumeup')

    elif 'bajar volumen' in comando:
        hablar('Bajando el volumen')
        for _ in range(5):
            pyautogui.press('volumedown')

    elif 'silencio' in comando:
        pyautogui.press('volumemute')
        hablar('Volumen silenciado')

    #Logica de Spotify
    elif 'reproduce' in comando or 'pon música de' in comando or 'pon' in comando:
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

    elif 'pausa' in comando or 'detén la musica' in comando or 'para la musica' in comando:
        try: sp.pause_playback(); hablar('Pausando')
        except: pass

    elif 'siguiente' in comando or 'siguiente canción' in comando:
        try: sp.next_track(); hablar('Siguiente canción') 
        except: pass

    #Logica de busqueda
    elif 'busca' in comando or 'busca en google' in comando:
        termino = comando.replace('busca', '').strip()
        hablar(f'Buscando {termino} en google')
        busqueda = f'https://www.google.com/search?q={termino}'
        hablar(f'Abriendo Google con información de {termino}')
        webbrowser.open(busqueda)

    #Este es el comando para que se desconecte
    elif 'descansa' in comando or 'adiós' in comando:
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
    iniciar_asistente()

