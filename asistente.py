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

#Carga las credenciales
load_dotenv()

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

def ejecutar_comando(comando):
    if not comando or comando == '':
        return 'continuar'
    
    #Estos son los comandos de aplicaciones
    if 'abrir youtube' in comando:
        hablar('Abriendo Youtube')
        webbrowser.open('https://www.youtube.com')

    elif 'abrir navegador' in comando:
        hablar('Abriendo Navegador')
        webbrowser.open('https://www.google.com')

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
            #Se busca la canción y el artista
            busqueda_track = sp.search(q=termino, limit=2, type='track')
            busqueda_artist = sp.search(q=termino, limit=1, type='artist')
            track_encontrado = busqueda_track['tracks']['items'][0] if busqueda_track['tracks']['items'] else None
            artista_encontrado = busqueda_artist['artists']['items'][0] if busqueda_artist['artists']['items'] else None

            #Si el nombre de la canción coincide mucho con lo que dijiste, prioriza la canción
            #Comparamos si el término está contenido exactamente en el nombre del artista
            if artista_encontrado and artista_encontrado['name'].lower() == termino.lower():
                #Si el usuario dijo exactamente el nombre de un artista
                artista_uri = artista_encontrado['uri']
                nombre_artista = artista_encontrado['name']
                sp.start_playback(context_uri=artista_uri)
                time.sleep(1)
                sp.shuffle(state=True)
                hablar(f'Listo, reproduciendo éxitos de {nombre_artista} en modo aleatorio')

            elif track_encontrado:
                #Si el usuario dijo exactamente el nombre de una canción
                #O lo que dijo conside mas con una canción
                track_uri = track_encontrado['uri']
                nombre_track = track_encontrado['name']
                nombre_artista_track = track_encontrado['artists'][0]['name']
                sp.start_playback(uris=[track_uri])
                time.sleep(1)
                sp.shuffle(state=True)
                hablar(f'Listo, reproduciendo {nombre_track} de {nombre_artista_track}')

            elif artista_encontrado:
                #Si el usuario dijo el nombre de una canción 
                #Pero coincide mas con el nombre de un artista 
                #(Esta es un caso aislado)
                sp.start_playback(context_uri=artista_encontrado['uri'])
                time.sleep(1)
                sp.shuffle(state=True)
                hablar(f'Reproduciendo exitos de {artista_encontrado['name']}')

            else:
                hablar('No encontre nada relacionado con la busqueda')
        except Exception as e:
            print(f'Error {e}')
            hablar('Hubo un error. Asegurate que Spotify esté abierto y activo')

    elif 'pausa' in comando or 'detén la música' in comando or 'para la música' in comando:
        try:
            sp.pause_playback()
            hablar('Música pausada')
        except:
            pass

    elif 'siguiente' in comando or 'siguiente canción' in comando:
        try:
            sp.next_track()
            hablar('Saltando a la siguiente')
        except:
            pass

    #Este es el comando para que se desconecte
    elif 'descansa' in comando or 'adiós' in comando:
        hablar('Hasta luego, que tengas un resto de buen día')
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

                hablar('Te escucho')
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
    iniciar_asistencia()
