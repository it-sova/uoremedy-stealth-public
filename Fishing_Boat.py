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

LOOT = [
    Types.GOLD,
    0x0DCA  # Fishing net
]

BOOTS = [
    0x170D,  # Sandals
    0x170B,  # Boots
    0x1711,  # Tight Boots
]

ENEMIES = [
    0x0096,  # Sea Serpent
]

MOVE_TO_CONTAINER = [
    
]

FISH_TO_CUT = [
    0x09CF,  # a Fish
    0x09CD,  # a Fish
    0x09CC,  # a Fish
    0x09CE,  # a Fish
    0x4303,  # Yellow Perch
    0x4307,  # Redbelly Bream
    0x4306,  # Bluegill Sunfish
    0x09CE,  # Uncommon Shiner
    0x4302,  # Fluke Fish
    0x44C6,  # Mahi Fish
    0x44C5,  # Mahi Fish
    0x44C4,  # Pike
    0x44E5,  # Halibut Fish
    0x44E6,  # Halibut Fish
    0x44C3,  # Bonefish
    0x4305,  # RedSnapper Fish
    0x4304,  # RedSnapper Fish

]


WATER_TILES = range(6038, 6044)


def cancel_targets():
    CancelWaitTarget()
    if TargetPresent():
        CancelTarget()


def trash_boots():
    for _boots_type in BOOTS:
        if FindType(_boots_type, Backpack()):
            for _boots in GetFoundList():
                MoveItem(_boots, 0, Ground(), GetX(Self()), GetY(Self()), -2)
                Wait(1000)


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
        print(f"There is {FindCount()} poles left")
    else:
        print("No more poles left")
        exit()


def check_enemy():
    for _enemy_type in ENEMIES:
        if FindType(_enemy_type, Ground()):
            _enemy = FindItem()
            UOSay("[arm")
            Wait(100)
            while IsObjectExists(_enemy):
                Attack(_enemy)

                if GetActiveAbility() != "Armor Ignore":
                    if Mana() > 30:
                        UsePrimaryAbility()

                _try = 0
                if HP() < MaxHP() - 10:
                    UOSay("[bandself")
                    Wait(500)
                    while InJournal("You finish|not damaged|heal|barely help") < 0:
                        _try += 1
                        if _try > 20:
                            print("Healing timeout")
                            break
                    ClearJournal()

                Wait(500)

            loot_corpse()


def loot_corpse():
    if FindType(0x2006, Ground()):
        print("Enemy")
        _corpse = FindItem()
        UseObject(_corpse)
        Wait(1000)
        for _loot in LOOT:
            if FindType(_loot, _corpse):
                Grab(FindItem(), 0)
                Wait(1000)
        Ignore(_corpse)


def find_tiles(center_x, center_y, radius):
    _min_x, _min_y = center_x-radius, center_y-radius
    _max_x, _max_y = center_x+radius, center_y+radius
    _tiles_coordinates = []
    for _tile in WATER_TILES:
        _tiles_coordinates += GetStaticTilesArray(_min_x, _min_y, _max_x, _max_y, WorldNum(), _tile)
    print("[FindTiles] Found "+str(len(_tiles_coordinates))+" tiles")
    return _tiles_coordinates


def fishing():
    for _tile_data in find_tiles(GetX(Self()), GetY(Self()), 4):
        _tile, _x, _y, _z = _tile_data
        print(f"X = {_x} Y = {_y} Z = {GetZ(Self()) - 3}")
        while not Dead():
            cut()
            # Broken somewhat..
            # trash_boots()
            #
            check_enemy()
            check_poles()
            cancel_targets()
            _started = dt.now()
            UseType(Types.FISHING_POLE, 0xFFFF)
            WaitForTarget(2000)
            if TargetPresent():
                WaitTargetTile(_tile, _x, _y, _z)
                WaitJournalLine(_started, "|".join(SKIP_TILE_MESSAGES+NEXT_TRY_MESSAGES), 15000)

                if dt.now() >= _started + timedelta(seconds=15):
                    print("WaitJournalLine timeout, bad tile")
                    break

                if InJournalBetweenTimes("|".join(SKIP_TILE_MESSAGES), _started, dt.now()) > 0:
                    break

            Wait(500)

        Wait(500)


while not Dead():
    fishing()
