import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

"""Datos de otros archivos"""
from config import SCOPES, EMAIL_SENDER, EMAIL_RECEIVER

gmail_service = None

def get_gmail_service():
    """
    Inicializa el servicio de Gmail para enviar correos.
    Verifica si las credenciales existen en 'token.json' y las refresca si es necesario.
    Si no existen, inicia el flujo de autorización.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    global gmail_service
    gmail_service = build('gmail', 'v1', credentials=creds)
    return gmail_service

def create_message(sender, to, subject, message_text):
    """Crea un mensaje en formato MIME (texto sin formato)."""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """Envía un mensaje de email."""
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print('An error occurred: %s' % error)

def send_email_notification(subject, body):
    """
    Crea el mensaje y envía una notificación 
    por correo electrónico.
    """
    global gmail_service
    if not gmail_service:
        print("Error: El servicio de Gmail no está inicializado.")
        return
    
    try:
        message = create_message(EMAIL_SENDER, EMAIL_RECEIVER, subject, body)
        send_message(gmail_service, 'me', message)
        print(f"Correo de notificación enviado")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
