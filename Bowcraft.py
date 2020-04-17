from py_stealth import *
from datetime import datetime as dt
TOOL_TYPE = 0x1022
TRASH = 0x400AC053
TOOL_BOX = 0x400809AA
BOARDS = 0x1BD7
#
CRAFT_TYPE = 0x27A5
CRAFT_CATEGORY = 15
CRAFT_BUTTON = 37
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
    if not FindTypeEx(BOARDS, 0x0000, Backpack(), False) or FindQuantity() < 100:
        if FindTypeEx(BOARDS, 0x0000, Ground(), False) and FindQuantity() > 200:
            print(f"Boards left -> {FindQuantity()-200}")
            MoveItem(FindItem(), 200, Backpack(), 0, 0, 0)
            Wait(1000)
        else:
            print("No more boards left")
            exit()
    else:
        if not FindType(TOOL_TYPE, Backpack()) or FindCount() < 3:
            UseObject(TOOL_BOX)
            Wait(1000)
            if FindType(TOOL_TYPE, TOOL_BOX) and FindCount() > 5:
                for _item in GetFindedList()[:3]:
                    MoveItem(_item, 0, Backpack(), 0, 0, 0)
                    Wait(1000)
                print(f"Tools left -> {FindCount()-3}")
            else:
                print("No more tools left")
                exit()

        # Select normal wood for crafting ( runs only once )
        if first_run == 1:
            UseType(TOOL_TYPE, 0x0000)
            wait_for_gump(7)
            wait_for_gump(6)
            wait_for_gump(0)
            first_run = 0

        craft_item(CRAFT_CATEGORY, CRAFT_BUTTON, TOOL_TYPE, CRAFT_TYPE, 1)
        if FindType(CRAFT_TYPE, Backpack()):
            for _item in GetFindedList():
                MoveItem(_item, 0, TRASH, 0, 0, 0)
                Wait(1000)
