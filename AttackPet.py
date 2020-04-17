from py_stealth import *

pet = 0x00008F38

print(GetHP(pet))
while not Dead():
    if IsObjectExists(pet):
        while GetHP(pet) > 10:
            if Mana() > 20:
                CastToObj("Magic Arrow", pet)
                Wait(3000)
            else:
                while Mana() < 20:
                    Wait(5000)
        Wait(10000)
    else:
        print("No pet found")
        PauseCurrentScript()