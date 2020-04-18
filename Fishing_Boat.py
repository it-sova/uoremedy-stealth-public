from py_stealth import *
from datetime import timedelta, datetime as dt
from Scripts.helpers import Types


SKIP_TILE_MESSAGES = [
    "cannot be seen",
    "The fish don't seem"

]

NEXT_TRY_MESSAGES = [
    "You fish a while",
    "You pull"
]

FISH_TO_CUT = [
    0x09CF, 0x09CD, 0x09CC, 0x09CE
]

WATER_TILES = range(6038, 6044)


def cancel_targets():
    CancelWaitTarget()
    if TargetPresent():
        CancelTarget()


def cut():
    if FindType(Types.DAGGER, Backpack()):
        for _fish in FISH_TO_CUT:
            if FindType(_fish, Backpack()):
                cancel_targets()
                UseType(Types.DAGGER, 0x0000)
                WaitForTarget(2000)
                WaitTargetType(_fish)
                Wait(1000)


def check_poles():
    if FindType(Types.FISHING_POLE, Backpack()):
        print(f"There is {FindQuantity()} poles left")
    else:
        print("No more poles left")
        exit()


def find_tiles(center_x, center_y, radius):
    _min_x, _min_y = center_x-radius, center_y-radius
    _max_x, _max_y = center_x+radius, center_y+radius
    _tiles_coordinates = []
    for _tile in WATER_TILES:
        _tiles_coordinates += GetStaticTilesArray(_min_x, _min_y, _max_x, _max_y, WorldNum(), _tile)
    print("[FindTiles] Found "+str(len(_tiles_coordinates))+" tiles")
    return _tiles_coordinates


def fishing():
    for _tile_data in find_tiles(GetX(Self()), GetY(Self()), 3):
        _tile, _x, _y, _z = _tile_data
        print(f"X = {_x} Y = {_y} Z = {GetZ(Self()) - 3}")
        while not Dead():
            cut()
            cancel_targets()
            _started = dt.now()
            UseType(Types.FISHING_POLE, 0xFFFF)
            WaitForTarget(2000)
            if TargetPresent():
                WaitTargetTile(_tile, _x, _y, _z)
                WaitJournalLine(_started, "|".join(SKIP_TILE_MESSAGES+NEXT_TRY_MESSAGES), 15000)

                if InJournalBetweenTimes("|".join(SKIP_TILE_MESSAGES), _started, dt.now()) > 0:
                    print("Point useless")
                    break

            Wait(500)

        Wait(500)

fishing()
