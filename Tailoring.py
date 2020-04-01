from py_stealth import *
from Scripts.helpers import Types
from datetime import datetime as dt

TOOL_BOX = 0x400809AA
#
CRAFT_TYPE = 0x2798
CRAFT_CATEGORY = 8
CRAFT_BUTTON = 100
#


def craft_item(tool_category, tool_button, tool_type, item_type, required_qty):
    while Count(item_type) < required_qty:
        for _gump_counter in range(0, GetGumpsCount()):
            CloseSimpleGump(_gump_counter)

        if FindType(tool_type, Backpack()):
            UseType(tool_type, 0x0000)
            Wait(500)
            wait_for_gump(tool_category)
            wait_for_gump(tool_button)
            wait_for_gump(0)


def find_gump(gump_id):
    for _gump in range(0, GetGumpsCount()):
        if GetGumpID(_gump) == gump_id:
            return True
    return False


def wait_for_gump(button):
    _try = 0
    _start = dt.now()
    while not find_gump(0x38920ABD):
        _try += 1
        Wait(500)

        # If tool broken there is no incoming gump
        if InJournalBetweenTimes("You have worn", _start, dt.now()) > 0:
            return

        if _try > 30:
            print(f"wait_for_gump timeout ({button})")
            return

    WaitGump(button)
    Wait(2000)


SetARStatus(True)
SetPauseScriptOnDisconnectStatus(True)
SetFindDistance(2)
ClearSystemJournal()
first_run = 1
while not Dead():
    if not FindTypeEx(Types.CUT_CLOTH, 0x0000, Backpack(), False) or FindQuantity() < 100:
        if FindTypeEx(Types.CUT_CLOTH, 0x0000, Ground(), False) and FindQuantity() > 200:
            print(f"Cloth left -> {FindQuantity()-200}")
            MoveItem(FindItem(), 200, Backpack(), 0, 0, 0)
            Wait(1000)
        else:
            print("No more cloth left")
            exit()
    else:
        if not FindType(Types.SEWING_KIT, Backpack()) or FindCount() < 3:
            UseObject(TOOL_BOX)
            Wait(1000)
            if FindType(Types.SEWING_KIT, TOOL_BOX) and FindCount() > 5:
                for _item in GetFindedList()[:3]:
                    MoveItem(_item, 0, Backpack(), 0, 0, 0)
                    Wait(1000)
                print(f"Tools left -> {FindCount()-3}")
            else:
                print("No more tools left")
                exit()

        if not FindType(Types.SCISSORS, Backpack()) or FindCount() < 3:
            UseObject(TOOL_BOX)
            Wait(1000)
            if FindType(Types.SCISSORS, TOOL_BOX) and FindCount() > 5:
                for _item in GetFindedList()[:3]:
                    MoveItem(_item, 0, Backpack(), 0, 0, 0)
                    Wait(1000)
                print(f"Scissors left -> {FindCount()-3}")
            else:
                print("No more scissors left")
                exit()


        if first_run == 1:
            UseType(Types.SEWING_KIT, 0x0000)
            wait_for_gump(7)
            wait_for_gump(6)
            wait_for_gump(0)
            first_run = 0

        craft_item(CRAFT_CATEGORY, CRAFT_BUTTON, Types.SEWING_KIT, CRAFT_TYPE, 1)
        if FindType(CRAFT_TYPE, Backpack()):
            for _item in GetFindedList():
                WaitTargetObject(_item)
                UseType(Types.SCISSORS, 0x0000)
                Wait(1000)


