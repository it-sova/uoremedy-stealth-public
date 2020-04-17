from py_stealth import *

UOSay("bank")
Wait(100)
CONTAINER = BankLayer()

FindType(-1, CONTAINER)
print(GetFoundList())