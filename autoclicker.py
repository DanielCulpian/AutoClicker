# Made by Daniel Culpian
import pyautogui, keyboard, time, subprocess
def main():
    try:
        running = True  # Variable para controlar el bucle
        first = False

        txt = 'Iniciando autoclicker, creado por: Daniel Culpian -> _culpi_'
        printResult = (f"echo {txt}")
        subprocess.call(printResult, shell=True)

        x, y = get_click_position()
        while running:
            if keyboard.is_pressed("space"):  # Verificar si se presionó la tecla Espacio
                txt = 'La tecla Espacio ha sido presionada. Deteniendo el programa.'
                printResult = (f"echo {txt}")
                subprocess.call(printResult, shell=True)

                running = False
            else:
                if first == False:
                    keyboard.wait("p")
                    first = True
                pyautogui.click(x, y)
                pass

    except KeyboardInterrupt:
        txt = 'Se detectó una interrupcion, parando el programa...'
        printResult = (f"echo {txt}")
        subprocess.call(printResult, shell=True)

def get_click_position():
    txt = 'Tienes 10 segundos para ubicar tu cursor en la zona donde quieres hacer autoclick'
    printResult = (f"echo {txt}")
    subprocess.call(printResult, shell=True)

    for i in range(0,10):
        txt = (i+1)
        printResult = (f"echo {txt}")
        subprocess.call(printResult, shell=True)

        time.sleep(1)
    x, y = pyautogui.position()

    txt = (f"Ubicacion de clic: X={x}, Y={y}")
    printResult = (f"echo {txt}")
    subprocess.call(printResult, shell=True)

    txt = ("Presiona la 'p' cuando quieras empezar!")
    printResult = (f"echo {txt}")
    subprocess.call(printResult, shell=True)

    txt = ("Presiona 'espacio' para detener el programa.")
    printResult = (f"echo {txt}")
    subprocess.call(printResult, shell=True)
    return x, y

if __name__ == "__main__":
    main()