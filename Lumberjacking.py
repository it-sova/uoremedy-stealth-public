from py_stealth import *
from datetime import timedelta, datetime as dt
from telegram.telegram import telegram_message
import re

CHEST_TOOLTIP_REGEX = r"(\d+)\/(\d+)\sstones"
POINTS = [
    (0, 3077, 90),
    (1, 3114, 86),
    (2, 3084, 125),
    (3, 3117, 117),
    (4, 3000, 188),
    (5, 3085, 165),
    (6, 3121, 163),
    (7, 3083, 192),
    (8, 3077, 234),
    (9, 2998, 245),
    (10, 2979, 291),
    (11, 2918, 337),
    (12, 2858, 375),
    (13, 2879, 414),
    (14, 2900, 454),
    (15, 2951, 416),
    (16, 2925, 376),
]
# Home
NEAR_HOME_POINT = (3030, 213)
INSIDE_GATE = (3028, 219)
OUTSIDE_GATE = (3029, 221)
GATE = 0x40044F08
CHEST = 0x09AB
HOME_CHEST = 0x4008C5A4
#
TREE_TILES = [
    3274, 3275, 3277, 3280,
    3283, 3286, 3288, 3290,
    3293, 3296, 3299, 3302,
    3320, 3323, 3326, 3329,
    3393, 3394, 3395, 3396,
    3415, 3416, 3417, 3418,
    3419, 3438, 3439, 3440,
    3441, 3442, 3460, 3461,
    3462, 3476, 3478, 3480,
    3482, 3484, 3492, 3496
]
# Common types
TINKER_TOOLS = 0x1EB8
AXE = 0x0F43
LOG = 0x1BDD
BOARDS = 0x1BD7
INGOTS = 0x1BF2
ELEMENTAL = 0x002F

MISC_ITEMS = [
    0x1BDD,
    0x2F5F,
    0x3199,
    0x3191,
    0x318F,
    0x3190,
    0x0EED
]
#

BAD_POINTS = []

# Messages to skip current tile (depleted, etc0
SKIP_TILE_MESSAGES = [
                "not enough",
                "You cannot",
]
# Messages to continue chopping
NEXT_TRY_MESSAGES = [
                     "You hack at",
                     "You put",
                     "You chop",
                     "You have worn"
]
# Messages to mark tile as bad
BAD_POINT_MESSAGES = [
                        "You can't use",
                        "be seen",
                        "is too far",
                        "no line of",
                        "axe on that",
]


def sort_trees(trees):
    _trees_by_distance = {}
    _ordered_trees_list = []
    _prev_last_tree = (0, NEAR_HOME_POINT[0], NEAR_HOME_POINT[1])

    def _tree_dist(_tree1, _tree2):
        return Dist(_tree1[1], _tree1[2], _tree2[1], _tree2[2])

    for _tree in trees:
        _td = _tree_dist(_tree, _prev_last_tree)
        if _td % 2 == 0:
            _td -= 1
        _trees_group = _trees_by_distance.get(_td, [])
        _trees_group.append(_tree)
        _trees_by_distance[_td] = _trees_group

    for current_distance in _trees_by_distance:
        _trees = _trees_by_distance[current_distance]
        first_tree = last_tree = _trees[0]
        for tree1 in _trees:
            for tree2 in _trees:
                if _tree_dist(tree1, tree2) > _tree_dist(first_tree, last_tree):
                    first_tree, last_tree = tree1, tree2
        if _tree_dist(_prev_last_tree, last_tree) < _tree_dist(_prev_last_tree, first_tree):
            first_tree, last_tree = last_tree, first_tree
        _trees.sort(key=lambda _tree: _tree_dist(_tree, first_tree))
        _ordered_trees_list += _trees
        _prev_last_tree = last_tree

    return _ordered_trees_list


def find_tiles(center_x, center_y, radius):
    _min_x, _min_y = center_x-radius, center_y-radius
    _max_x, _max_y = center_x+radius, center_y+radius
    _tiles_coordinates = []
    for _tile in TREE_TILES:
        _tiles_coordinates += GetStaticTilesArray(_min_x, _min_y, _max_x, _max_y, WorldNum(), _tile)
    print("[FindTiles] Found "+str(len(_tiles_coordinates))+" tiles")
    return _tiles_coordinates


def populate_trees_array():
    _trees = []
    for point in POINTS:
        (_point_number, _x, _y, _z) = point
        if NewMoveXY(_x, _y, True, 0, True):
            for _tree_tuple in find_tiles(_x, _y, 18):
                _trees.append(_tree_tuple)
        else:
            print("Can't get to point location, skipping")
    return _trees


def find_suitable_chest():
    # Trying to find not fully loaded chest
    if FindType(CHEST, Ground()):
        for _chest in GetFindedList():
            _tooltip = GetTooltip(_chest)
            _matches = re.search(CHEST_TOOLTIP_REGEX, _tooltip)
            # Chest for sure
            _chest_current_weight = _matches.group(1)
            _chest_maximum_weight = _matches.group(2)
            print(f"{_chest_current_weight}/{_chest_maximum_weight}")
            if _chest_current_weight+Weight() < _chest_maximum_weight:
                print("Using this chest to unload")
                return _chest

    return False


def unload(x, y):
    (_home_x, _home_y) = NEAR_HOME_POINT
    (_inside_gate_x, _inside_gate_y) = INSIDE_GATE
    (_outside_gate_x, _outside_gate_y) = OUTSIDE_GATE
    print("Heading to home")
    # newMoveXY(_home_x, _home_y, True, 0, True)
    newMoveXY(_inside_gate_x, _inside_gate_y, True, 0, True)
    Wait(1000)
    UseObject(GATE)
    # If find_suitable_chest ... else - no more suitable chests left, exit + telegram
    newMoveXY(_home_x, _home_y, True, 0, True)
    UseObject(HOME_CHEST)

    # Unload to find_suitable_chest
    if FindType(BOARDS, Backpack()):
        for _board in GetFindedList():
            MoveItem(_board, 0, HOME_CHEST, 0, 0, 0)
            Wait(1000)

    # Unload to find_suitable_chest
    for _misc_item in MISC_ITEMS:
        if FindType(_misc_item, Backpack()):
            MoveItem(FindItem(), 0, HOME_CHEST, 0, 0, 0)
            Wait(1000)

    # Still using HOME_CHEST
    if not FindType(INGOTS, Backpack()) or FindFullQuantity() < 150:
        if FindType(INGOTS, HOME_CHEST) and FindFullQuantity() > 200:
            print(f"Ingots left in chest => {FindFullQuantity()}")
            MoveItem(FindItem(), 150, Backpack(), 0, 0, 0)
            Wait(1000)
        else:
            print("No more ingots in home chest!")
            telegram_message("No more ingots in chest!")
            exit()

    # Useless?
    _tooltip = GetTooltip(HOME_CHEST)
    _matches = re.search(CHEST_TOOLTIP_REGEX, _tooltip)
    telegram_message(f"Current chest weight limit: {_matches.group(0)}")
    #
    craft_item(22, 128, TINKER_TOOLS, TINKER_TOOLS, 2)
    craft_item(22, 135, TINKER_TOOLS, AXE, 5)
    print("Heading to forest")
    newMoveXY(_outside_gate_x, _outside_gate_y, True, 0, True)
    Wait(1000)
    UseObject(GATE)
    newMoveXY(x, y, True, 0, True)


def cancel_targets():
    CancelWaitTarget()
    if TargetPresent():
        CancelTarget()


def check_and_equip_tool():
    if not ObjAtLayer(LhandLayer()):
        UOSay("[armtool 1")
        Wait(500)


def cut_logs():
    if FindType(LOG, Backpack()):
        for _log in GetFindedList():
            cancel_targets()
            WaitTargetObject(_log)
            UseObject(ObjAtLayer(LhandLayer()))
            WaitForTarget(1200)
            Wait(1200)


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
    while not find_gump(0x38920ABD):
        _try += 1
        Wait(500)
        if _try > 30:
            # print("wat_for_gump timeout")
            return

    WaitGump(button)
    Wait(2000)


def remove_duplicates(array):
    return list(set([i for i in array]))


def get_sorted_trees():
    _result = sort_trees(remove_duplicates(populate_trees_array()))
    print(f"Trees after duplicate removal => {len(_result)}")
    return _result


def check_elemental():

    if FindType(ELEMENTAL, Ground()):
        _enemy = FindItem()
        telegram_message(f"Elemental found: {GetName(_enemy)}")
        AddToSystemJournal(f"Elemental found: {GetName(_enemy)}")
        while FindType(ELEMENTAL, Ground()):
            if not Dead():
                while IsObjectExists(_enemy):
                    Attack(_enemy)
                    # To get rid of error "MoveXYZ failed"
                    if IsObjectExists(_enemy):
                        newMoveXY(GetX(_enemy), GetY(_enemy), True, 1, True)

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
                            # To get rid of error "MoveXYZ failed"
                            if IsObjectExists(_enemy):
                                newMoveXY(GetX(_enemy), GetY(_enemy), True, 1, True)

                            Wait(1000)
                        ClearJournal()
            else:
                AddToSystemJournal(f"Character dead. Enemy name -> {GetName(_enemy)} X:{GetX(Self())} Y:{GetY(Self())}")
                telegram_message(f"Character dead. Enemy name -> {GetName(_enemy)} X:{GetX(Self())} Y:{GetY(Self())}")
                break

            Wait(500)
        #
        loot_corpse()


def loot_corpse():
    if FindType(0x2006, Ground()):
        print("Elemental slain")
        _corpse = FindItem()
        # Trying to get rid of "invalid picked up item" error
        newMoveXY(GetX(_corpse), GetY(_corpse), True, 0, True)
        UseObject(_corpse)
        Wait(1000)
        for _misc_item in MISC_ITEMS:
            if FindType(_misc_item, _corpse):
                # MoveItem(FindItem(), 0, Backpack(), 0, 0, 0)
                # Trying to get rid of "invalid picked up item" error
                Grab(FindItem(), 0)
                Wait(1000)
        Ignore(_corpse)


def lumberjacking(sorted_trees):
    for _t, _x, _y, _z in sorted_trees:
        if ([_x, _y] not in BAD_POINTS) and NewMoveXY(_x, _y, True, 1, True):
            if Dead():
                newMoveXY(INSIDE_GATE[0], INSIDE_GATE[1], True, 0, True)
                SetWarMode(True)
                print(f"Character dead X:{GetX(Self())} Y:{GetY(Self())}")
                telegram_message(f"Character dead X:{GetX(Self())} Y:{GetY(Self())}")
                exit()

            while not Dead():
                # Preparations
                _starting_ts = dt.now()
                cancel_targets()
                # Check if axe equipped
                check_and_equip_tool()
                # Check for wooden elemental
                check_elemental()
                # Check if we are overloaded
                if Weight() > MaxWeight()-100:
                    cut_logs()
                    if Weight() > MaxWeight()-50:
                        unload(GetX(Self()), GetY(Self()))
                #
                UseObject(ObjAtLayer(LhandLayer()))
                WaitForTarget(2000)
                if TargetPresent():
                    WaitTargetTile(_t, _x, _y, _z)
                    WaitJournalLine(_starting_ts, "|".join(NEXT_TRY_MESSAGES+SKIP_TILE_MESSAGES+BAD_POINT_MESSAGES),
                                    15000)

                    # If we waited full WaitJournalLine timeout, something went wrong
                    if dt.now() >= _starting_ts+timedelta(seconds=15):
                        # print(f"{_x} {_y} WaitJournalLine timeout exceeded, bad tree?")
                        break

                    if InJournalBetweenTimes("|".join(BAD_POINT_MESSAGES), _starting_ts, dt.now()) > 0:
                        if [_x, _y] not in BAD_POINTS:
                            print(f"Added tree to bad points, trigger => {BAD_POINT_MESSAGES[FoundedParamID()]}")
                            BAD_POINTS.append([_x, _y])
                            break

                    if InJournalBetweenTimes("|".join(SKIP_TILE_MESSAGES), _starting_ts, dt.now()) > 0:
                        # print("Tile depleted, skipping")
                        break
                else:
                    print("No target present for some reason...")
                Wait(500)


# Start
ClearSystemJournal()
SetARStatus(True)
SetMoveOpenDoor(True)
SetPauseScriptOnDisconnectStatus(True)
IgnoreReset()
SetFindDistance(25)
# If script stopped unexpectedly - there can be logs in pack
cut_logs()
unload(OUTSIDE_GATE[0], OUTSIDE_GATE[1])
sorted_trees_array = get_sorted_trees()
while not Dead():
    lumberjacking(sorted_trees_array)
    Wait(1000)