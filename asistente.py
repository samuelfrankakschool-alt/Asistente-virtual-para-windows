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
    if 'abrir youtube' in comando or 'abre youtube' in comando:
        hablar('Abriendo Youtube')
        webbrowser.open('https://www.youtube.com')

    elif 'abrir navegador' in comando or 'abre el navegador' in comando:
        hablar('Abriendo Navegador')
        webbrowser.open('https://www.google.com')

    elif 'abrir notas' in comando or 'abre mis notas' in comando:
        hablar('Abriendo Notas')
        webbrowser.open('https://site2.q10.com/User/Login')

    elif 'abrir calculadora' in comando or 'abre la calculadora' in comando:
        hablar('Abriendo Calculadora')
        subprocess.Popen('calc.exe')
    
    elif 'abrir spotify' in comando or 'abre spotify' in comando:
        hablar('Abriendo Spotify')
        os.system('start spotify')

    #Estos son los comandos del sistema
    elif 'subir volumen' in comando or 'sube el volumen' in comando:
        hablar('Subiendo el volumen')
        for _ in range(5):
            pyautogui.press('volumeup')

    elif 'bajar volumen' in comando or 'baja el volumen' in comando:
        hablar('Bajando el volumen')
        for _ in range(5):
            pyautogui.press('volumedown')

    elif 'silencio' in comando or 'silencia' in comando:
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

    #Logica de busqueda
    elif 'busca en youtube' in comando:
        termino = comando.replace('busca en youtube', '').strip()
        hablar(f'Buscando {termino} en youtube')
        busqueda_youtube = f'https://www.youtube.com/results?search_query={termino}'
        hablar(f'Abriendo Youtube con tu busqueda')
        webbrowser.open(busqueda_youtube)

    elif 'busca en google' in comando or 'busca' in comando:
        termino = comando.replace('busca en google', '').replace('busca', '').strip()
        hablar(f'Buscando {termino} en google')
        busqueda = f'https://www.google.com/search?q={termino}'
        hablar(f'Abriendo Google con información de {termino}')
        webbrowser.open(busqueda)

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
