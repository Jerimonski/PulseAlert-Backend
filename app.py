import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
import pyodbc

"""Funciones de otros archivos"""
from notifications import get_gmail_service
from device_manager import devices, fetch_devices, check_status_and_notify_sync

app = Flask(__name__, static_folder='Front', static_url_path='')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-LU8KOHGC\\SQLEXPRESS02;DATABASE=DispositivosMuni;Trusted_Connection=yes;'
def get_db_cursor():
    try:
        conn = pyodbc.connect(connection_string)
        return conn, conn.cursor()
    except pyodbc.Error as ex:
        print(f"Error de conexión a la base de datos: {ex}")
        return None, None

# AÑADIDO: Ruta para servir el frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# MODIFICADO: Mueve el endpoint de la API a una ruta específica, ej. '/api/devices'
@app.route('/devices', methods=['GET'])
def get_devices():
    return jsonify(devices)

@app.route('/postDevices', methods=['POST'])
def add_devices():
    data = request.get_json()
    nombre = data['nombre']
    ip = data['ip']
    localizacion = data['localizacion']
    conn, cursor = get_db_cursor()

    try:
        cursor.execute("INSERT INTO DispositivosMuni (nombre, ip, localizacion) VALUES (?, ?, ?)", nombre, ip, localizacion)
        conn.commit()
        fetch_devices()
        return jsonify({"message": f"Dispositivo `{nombre}` agregado exitosamente"}), 201
    except pyodbc.Error as ex:
        return jsonify({"error": f"Error al insertar en la base de datos: {ex}"}), 500
    finally:
        if conn:
            conn.close()

# MODIFICADO: Cambia las rutas de actualización y borrado a '/api/devices/<string:ip>'
@app.route('/api/devices/<string:ip>', methods=['PATCH'])
def update_device(ip):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos de actualización no proporcionados"}), 400

    updates = []
    params = []

    if 'nombre' in data:
        updates.append("nombre = ?")
        params.append(data['nombre'])
    if 'ip' in data:
        updates.append("ip = ?")
        params.append(data['ip'])
    if 'localizacion' in data:
        updates.append("localizacion = ?")
        params.append(data['localizacion'])

    if not updates:
        return jsonify({"error": "No hay campos válidos para actualizar"}), 400
    
    params.append(ip)
    query = "UPDATE DispositivosMuni SET " + ", ".join(updates) + " WHERE ip = ?"

    conn, cursor = get_db_cursor()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor.execute(query, *params)
        if cursor.rowcount == 0:
            return jsonify({"error": f"No se encontró un dispositivo con el ip '{ip}'"}), 404
        
        conn.commit()
        fetch_devices() 
        return jsonify({"message": f"Dispositivo '{ip}' actualizado exitosamente"}), 200
    except pyodbc.Error as ex:
        return jsonify({"error": f"Error al actualizar en la base de datos: {ex}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/devices/<string:ip>', methods=['DELETE'])
def delete_device(ip):
    conn, cursor = get_db_cursor()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor.execute("DELETE FROM DispositivosMuni WHERE ip = ?", ip)
        if cursor.rowcount == 0:
            return jsonify({"error": f"No se encontró un dispositivo con el ip '{ip}'"}), 404
        
        conn.commit()
        fetch_devices()
        return jsonify({"message": f"Dispositivo '{ip}' eliminado exitosamente"}), 200
    except pyodbc.Error as ex:
        return jsonify({"error": f"Error al eliminar en la base de datos: {ex}"}), 500
    finally:
        if conn:
            conn.close()

@socketio.on('connect')
def handle_connect():
    """Maneja la conexión de un cliente WebSocket y envía el estado actual."""
    if devices:
        emit('status_update', {'devices': devices}, room=request.sid)

if __name__ == '__main__':
    get_gmail_service()
    fetch_devices()

    """BackgroundSheduler sirve para poder definir un intervalo
        de mandado de datos.
        scheduler para iniciar el software"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: check_status_and_notify_sync(socketio), trigger="interval", seconds=10)
    scheduler.start()
    
    socketio.run(app, port=5000)
