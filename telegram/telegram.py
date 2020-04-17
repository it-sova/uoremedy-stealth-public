from py_stealth import *
ID = 1
TOKEN = 'your-token-here'
USER_ID = 'your-user-here'


def telegram_message(message):
    MessengerSetToken(ID, TOKEN)
    MessengerSetConnected(ID, True)
    while not MessengerGetConnected(ID):
        Wait(100)

    _current_script = CurrentScriptPath().split("\\")
    MessengerSendMessage(ID, f"[{CharName()}] ({_current_script[-1]}) {message}", USER_ID)
    Wait(5000)
    MessengerSetConnected(ID, False)
