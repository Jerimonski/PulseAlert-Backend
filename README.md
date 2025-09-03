<div align="center">
<h1 align="center">Estados de red en tiempo real (Backend)</h1>
</div>

<!-- ACERCA DEL PROYECTO -->

## Acerca del proyecto
Este proyecto de backend es el cerebro detrás del sistema de monitoreo. Su función principal es realizar pings en tiempo real a una lista de direcciones IP predefinidas para verificar su estado de conexión. Si un dispositivo deja de responder, el sistema envía una notificación inmediata por correo electrónico. Utiliza WebSockets para comunicar el estado de cada dispositivo al frontend, permitiendo una visualización instantánea y actualizada.

### Motivos del proyecto:

* Monitoreo automatizado y en tiempo real de una cantidad variable de dispositivos.

* Notificación inmediata y automática por correo electrónico al detectar un fallo.

* Comunicación bidireccional y en tiempo real con el frontend para una experiencia de usuario fluida.

## Desarrollado con:
### Tecnologías
* ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
* ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
* ![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)

<!-- PREPARACIÓN ANTES DEL CÓDIGO -->

## Preparación antes del código
### Clona el repositorio:

1. Clonacion del repositorio:
   ```sh
    git clone https://github.com/Jerimonski/Check-Ping.git
   ```
2. Instala los paquetes de Python necesarios:
  ```sh
    pip install Flask Flask-SocketIO requests google-api-python-client google-auth-oauthlib
   ```
### Configuracion de la API de Gmail y credenciales de Google Cloud
Para que el backend pueda enviar correos de notificación, necesitas configurar la Gmail API. Sigue estos pasos para obtener las credenciales necesarias, las cuales no están incluidas en el repositorio por motivos de seguridad.

⚠️ Importante: Debes usar una cuenta de Google Cloud de empresa para este proyecto, ya que las cuentas personales pueden tener restricciones que impidan la correcta autenticación.

1. Ve a la Google Cloud Console.

2. Crea un nuevo proyecto o selecciona uno existente.

3. Habilita la API de Gmail.

4. En la sección "Credenciales", crea una credencial de tipo ID de cliente de OAuth.

5. Configura la pantalla de consentimiento de OAuth con la información de tu aplicación.

6. Descarga el archivo credentials.json y colócalo en la misma carpeta que el archivo principal del proyecto.

La primera vez que ejecutes la aplicación, se abrirá una ventana del navegador para que inicies sesión en tu cuenta de Gmail y otorgues los permisos necesarios. Esto generará automáticamente el archivo token.json para futuras autenticaciones.

<!-- MODO DE USO -->

## Modo de uso
### Ejecucion y despliegue local:

Este proyecto está diseñado para funcionar de forma local en el puerto 5000. El servidor del backend también sirve el frontend, lo que significa que no necesitas iniciar un servidor separado para el frontend.

1. Una vez tengas las credenciales configuradas, inicia la aplicación Python desde tu terminal:
   ```sh
      python app.py
   ```
2. Acceso local: El servidor se ejecutará en http://localhost:5000. Al acceder a esta dirección en tu navegador, el backend cargará la interfaz de usuario que se encuentra en una carpeta local (/Front o el nombre que le pongas a la carpeta del frontend).

3. Funcionamiento en tiempo real:
* El sistema comenzará a hacer pings a los dispositivos en un hilo en segundo plano.
* Si un dispositivo deja de responder, se enviará una notificación por correo electrónico.
* El estado de cada dispositivo se actualizará en tiempo real y se transmitirá a través de WebSockets, permitiendo que el frontend refleje los cambios al instante.

### Base de datos
La bd esta creada en SQL 2019 y compuesta por 1 tabla con las siguientes columnas nombre, ip, id y localizacion. Esta debe ser levantada de manera local y en caso de configuraciones como la eliminacion o edicion de columnas, se deben actualizar tanto las querys del back como las conexiones del front.
