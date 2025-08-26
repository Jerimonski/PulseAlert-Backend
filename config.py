import platform

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
EMAIL_SENDER = "jeremy.amaru.ayaviri@alumnos.uta.cl"
EMAIL_RECEIVER = "jeremy.amaru.ayaviri@alumnos.uta.cl"

PING_COMMAND = ["ping"]
if platform.system().lower() == "windows":
    PING_COMMAND.extend(["-n", "1"])
else:
    PING_COMMAND.extend(["-c", "1"])
