"""CRUDDDDDD"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler

"""Funciones de otros archivos"""
from notifications import get_gmail_service
from device_manager import devices, fetch_devices, check_status_and_notify_sync

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

"""ruta principal donde se conectara el frontend (Endpoint)"""
@app.route('/')
def index():
    return (devices)

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
    scheduler.add_job(func=lambda: check_status_and_notify_sync(socketio), trigger="interval", seconds=30)
    scheduler.start()
    
    socketio.run(app, debug=True, port=5000)

    """
    comando para iniciar la bd
    sqlcmd -S LAPTOP-LU8KOHGC\SQLEXPRESS02 -E
    """
