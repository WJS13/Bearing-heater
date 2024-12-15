import flet as ft
import threading
import time
import serial

# Conexión Arduino
try:
    ser = serial.Serial('COM4', 9600, timeout=1)
except serial.SerialException as e:
    print(f"Error al abrir el puerto: {e}")
    exit()

# Tiempos de detención 
tiempos_rodamiento = {
    "6308": 60,  
    "6302": 100,  
    "6205": 90,  
    "6010": 150,  
    "6403": 110, 
    "Otro material": None 
}

def main(page: ft.Page):
    page.title = "Calentadora de Rodamientos"
    
    # Configuración de la ventana
    page.window.width = 500
    page.window.height = 500
    page.window.resizable = False
    page.window.maximizable = False
    page.window.minimizable = False  
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Variables de temperatura
    temperatura_inicial = 25  # Temperatura inicial fija
    temperatura_final = ft.Text(value="Temperatura Final: --°C")
    temperatura_actual = ft.Text(value=f"Temperatura Actual: {temperatura_inicial}°C")  # Inicialmente se muestra 25°C
    contador_tiempo = ft.Text(value="Tiempo restante: --")

    detener_hilo = False

    def actualizar_temperatura():
        global temperatura_actual
        while not detener_hilo:
            ser.write(b'T')  
            temperatura_serial = ser.readline().decode('utf-8').strip()
            if temperatura_serial:
                try:
                    temperatura_actual_value = float(temperatura_serial.split(':')[1].replace(" C", "").strip())
                    temperatura_actual.value = f"Temperatura Actual: {temperatura_actual_value}°C"
                    page.update()
                except ValueError:
                    pass
            time.sleep(1)

    def iniciar_calentamiento(e):
        global detener_hilo
        detener_hilo = False

        rodamiento = rodamiento_selector.value
        tiempo = tiempos_rodamiento.get(rodamiento)

        # Validación del tiempo ingresado
        if rodamiento == "Otro material":
            try:
                tiempo = int(tiempo_input.value)
                if tiempo <= 0:
                    raise ValueError("El tiempo debe ser un número positivo.")
            except ValueError as e:
                print(f"Error en el tiempo ingresado: {e}")
                return
        else:
            tiempo = tiempos_rodamiento[rodamiento]

        ser.write(b'1')  
        threading.Thread(target=actualizar_temperatura, daemon=True).start()

        def cuenta_regresiva():
            nonlocal tiempo
            while tiempo > 0 and not detener_hilo:
                contador_tiempo.value = f"Tiempo restante: {tiempo} segundos"
                page.update()
                time.sleep(1)
                tiempo -= 1

            if not detener_hilo:
                temperatura_final.value = f"Temperatura Final: {temperatura_actual.value.split(': ')[1]}"  # Muestra la temperatura actual al finalizar
                enviar_notificacion_bot(f"El rodamiento {rodamiento} alcanzó {temperatura_actual.value.split(': ')[1]}.")
                ser.write(b'0')

        threading.Thread(target=cuenta_regresiva, daemon=True).start()

    def detener_calentamiento(e):
        global detener_hilo
        detener_hilo = True
        print("Calentamiento detenido")
        enviar_notificacion_bot("El proceso ha sido detenido.")
        ser.write(b'0') 

    def enviar_notificacion_bot(mensaje):
        print(f"Notificación al bot: {mensaje}")

    def actualizar_tiempo(e):
        rodamiento = rodamiento_selector.value
        if rodamiento in tiempos_rodamiento and tiempos_rodamiento[rodamiento] is not None:
            tiempo_input.value = str(tiempos_rodamiento[rodamiento])
        else:
            tiempo_input.value = ""  # Dejar vacío para "Otro material"
        page.update()

    rodamiento_selector = ft.Dropdown(
        label="Seleccionar tipo de rodamiento",
        options=[
            ft.dropdown.Option("6308"),
            ft.dropdown.Option("6302"),
            ft.dropdown.Option("6205"),
            ft.dropdown.Option("6010"),
            ft.dropdown.Option("6403"),
            ft.dropdown.Option("Otro material "),
        ],
        value="",  
        on_change=actualizar_tiempo  # Llama a la función al cambiar la selección
    )

    tiempo_input = ft.TextField(label="Tiempo (segundos)", value="")
    iniciar_btn = ft.ElevatedButton(text="Iniciar", on_click=iniciar_calentamiento)
    detener_btn = ft.ElevatedButton(text="Detener", on_click=detener_calentamiento)

    # Añadir a la página
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("CALENTADOR DE RODAMIENTOS", size=24, weight="bold", text_align="center", color='pink'),
                    rodamiento_selector,
                    tiempo_input,
                    temperatura_actual,
                    contador_tiempo,
                    temperatura_final,
                    ft.Row([iniciar_btn, detener_btn], alignment=ft.MainAxisAlignment.CENTER),
                ],
                alignment=ft.MainAxisAlignment.START,  
                spacing=20,
            ),
            padding=20,
            width=400,
            height=400,
            alignment=ft.alignment.top_center,
        )
    )

ft.app(target=main)