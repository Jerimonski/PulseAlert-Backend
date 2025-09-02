import asyncio
import subprocess
import pyodbc
from datetime import datetime

"""Funciones de otros archivos"""
from config import PING_COMMAND
from notifications import send_email_notification

devices = []

def fetch_devices():
    """Obtiene la lista de dispositivos de la API y actualiza 
    la variable global."""
    global devices
    connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-LU8KOHGC\SQLEXPRESS02;DATABASE=DispositivosMuni;Trusted_Connection=yes;'
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, ip, localizacion FROM DispositivosMuni")

        """status puede ser: Desconocido, Activo, Caido
            active puede ser: Perdido/s, Econtrado"""

        devices = [{
            "name": item.nombre,
            "ip": item.ip,
            "localizacion": item.localizacion,
            "status": "Desconocido",    
            "active": "Perdido/s",      
            "down_count": 0
        } for item in cursor]
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}")
    finally:
        # Close the connection
        if 'conn' in locals() and conn:
            conn.close()

async def ping_device_async(device):
    """
    Función asíncrona para hacer un solo ping.
    Utiliza asyncio.to_thread para no bloquear el bucle de eventos.
    """
    try:
        result = await asyncio.to_thread(
            subprocess.run,
            PING_COMMAND + [device['ip']], 
            capture_output=True, 
            text=True, 
            timeout=3
        )
        return "Activo" if result.returncode == 0 else "Desconocido"
    except (subprocess.TimeoutExpired, Exception):
        return "Desconocido"

def check_status_and_notify_sync(socketio):
    """
    Verifica el estado de los dispositivos, actualiza su estado y notifica.
    Esta función se ejecuta de forma síncrona en el BackgroundScheduler.
    """
    global devices
    
    if not devices:
        fetch_devices()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        """Obtiene los nuevos estados, Activo, 
        Caido o Perdido/s"""
    new_statuses = loop.run_until_complete(
        asyncio.gather(*[ping_device_async(device) for device in devices])
    )
    
    off_devices_for_email = []
    
    """Condicionales para determinar si un dispositivo esta Caido
        o no, y empezar el conteo para mandar el aviso por email"""
    for i, new_status in enumerate(new_statuses):
        devices[i]['status'] = new_status
        if new_status == "Activo":
            devices[i]['active'] = "Encontrado" 
            devices[i]['down_count'] = 0

        if devices[i]["active"] == "Encontrado" and new_status != "Activo": 
            devices[i]["status"] = "Caido"
        # 
        if devices[i]["status"] == "Caido" and devices[i]['active'] == "Encontrado":
            devices[i]['down_count'] += 1
            print(devices[i]["name"], "count_down", devices[i]["down_count"])
        else:
            devices[i]['down_count'] = 0
        
        if devices[i]['down_count'] == 10:
            off_devices_for_email.append(devices[i])
            devices[i]['down_count'] = 0
            devices[i]['active'] = "Perdido/s"
            devices[i]['status'] = "Desconocido"

    """Aqui se mandan los nuevos estados al frontend"""
    socketio.start_background_task(target=lambda: socketio.emit('status_update', {'devices': devices}))
    
    """Si en el array de Dispositivos Caidos existe alguno
        o algunos, entonces se forma el email y se manda"""
    if off_devices_for_email:
        fallDevices = [f"{item['name']} ({item['ip']})" for item in off_devices_for_email]
        subject = f"⚠️ Dispositivo/s CAÍDO/S"
        body = 'Dispositivos confirmados como caídos:\n\n' + f'\n {datetime.now()}\n\n'.join(fallDevices)
        send_email_notification(subject, body) 
        print("Notificación de caída enviada.")
        for device in off_devices_for_email:
            device['down_count'] = 0
