import speech_recognition as sr
import pyttsx3
import subprocess
import webbrowser
import pyautogui
import keyboard
import time

#Configuración de voz
engine = pyttsx3.init()
voices = engine.getProperty('voices')
#Aqui se elije el tono de voz (0 = Masculino y 1 = Femenino)
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 185) #Velocidad del habla

def hablar(texto):
    print(f'Asistente: {texto}')
    engine.say(texto)
    engine.runAndWait()

def escucha():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print('Escuchando...')
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print('Procesando voz...')
            comando = r.recognize_google(audio, language='es-CO')
            print(f'Dijiste {comando}')
            return comando.lower()
        except Exception:
            return ''
        
def ejecutar_comando(comando):
    if not comando:
        return
    
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
    elif 'descansa' in comando or 'adios' in comando:
        hablar('Hasta luego, que tengas un resto de buen día')
        return 'salir'
    
    return 'continuar'

#Bucle principal
def iniciar_asistencia():
    print('>>> ASISTENTE ACTIVO <<<')
    print('Instrucciones: Precionar la tecla "ALT" para hablar')

    while True:
        #El asistente espera a que precione la tecla ALT
        if keyboard.is_pressed('alt'):
            hablar('Te estoy escuchando...')
            pedido = escucha()
            estado = ejecutar_comando(pedido)

            if estado == 'salir':
                break

            print('\nEsperando activación (Preciona ALT)...')
            time.sleep(0.5) #Esto evita activaciones multiples

if __name__ == '__main__':
    iniciar_asistencia()
