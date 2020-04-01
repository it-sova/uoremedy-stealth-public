from py_stealth import *
from Scripts.helpers import Types
from datetime import datetime as dt

LOCKPICK_CHEST = 0x4003EA52
#
CRAFT_TYPE = 0x14FC
CRAFT_CATEGORY = 22
CRAFT_BUTTON = 233
CRAFT_TOOL_BUTTON = 128
CRAFT_TOOL_CATEGORY = 22
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
    if not FindTypeEx(Types.INGOT, 0x0000, Backpack(), False) or FindQuantity() < 100:
        if FindTypeEx(Types.INGOT, 0x0000, Ground(), False) and FindQuantity() > 200:
            print(f"Ingots left -> {FindQuantity()-200}")
            MoveItem(FindItem(), 200, Backpack(), 0, 0, 0)
            Wait(1000)
        else:
            print("No more ingots left")
            exit()
    else:
        if first_run == 1:
            UseType(Types.TINKER_TOOLS, 0x0000)
            wait_for_gump(7)
            wait_for_gump(6)
            wait_for_gump(0)
            first_run = 0

        craft_item(CRAFT_TOOL_CATEGORY, CRAFT_TOOL_BUTTON, Types.TINKER_TOOLS, Types.TINKER_TOOLS, 2)
        craft_item(CRAFT_CATEGORY, CRAFT_BUTTON, Types.TINKER_TOOLS, CRAFT_TYPE, 1)
        if FindType(CRAFT_TYPE, Backpack()):
            for _item in GetFindedList():
                MoveItem(_item, 0, LOCKPICK_CHEST, 0, 0, 0)
                Wait(1000)
    Wait(100)

