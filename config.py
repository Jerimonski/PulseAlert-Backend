import platform

SCOPES = ['googleApi']
EMAIL_SENDER = "example@gmail.com"
EMAIL_RECEIVER = "example@gmail.com"

PING_COMMAND = ["ping"]
if platform.system().lower() == "windows":
    PING_COMMAND.extend(["-n", "1"])
else:
    PING_COMMAND.extend(["-c", "1"])
