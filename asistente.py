import speech_recognition as sr
import pyttsx3
import subprocess
import webbrowser
import pyautogui
import keyboard
import time


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
        print('Escuchando...')
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
