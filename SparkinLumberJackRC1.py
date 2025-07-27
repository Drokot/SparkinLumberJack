# This is a Semi-Auto Lumberjacking Script
# by Sparkin 5/2025
# Original Script was modified by Grok
# Modified by Grok to support up to 5 pack animals, 7/2025
# Added credit to Kurien33 for testing and development help, 7/2025
# Special thanks to Kurien33 for many hours of testing and development help

# System Variables
from System.Collections.Generic import List
from System import Byte, Int32
import clr
clr.AddReference('System.Speech')
from System.Speech.Synthesis import SpeechSynthesizer
from math import sqrt
import random

# Configuration
packAnimals = [
    {'serial': 0x043D5FC2, 'type': 'beetle'},  # Pack Animal for logs/boards
    {'serial': 0x09B6F6B9, 'type': 'beetle'},
    {'serial': 0x09B6F26D, 'type': 'beetle'},
  # {'serial': 0x09B6F3B1, 'type': 'beetle'},
  # {'serial': 0x09B87679, 'type': 'beetle'},
]  # List of pack animals (up to 5, with serial and type)

logsToBoards = True  # If you want boards
treeCooldown = 1200000  # 20 minutes
alert = False  # ON is Safe
scanRadius = 20  # Tiles
axeSerial = 0x640C2454  # Your axe ID
logBag = 0x5A01E7ED  # Use backpack ID
otherResourceBag = 0x40191C19  # If needed
weightLimit = Player.MaxWeight - 10  # Stones under max
dragDelay = 800
beetleWeightLimit = 1600  # Pack animal weight limit (same for all)
mountAfterMove = False  # Set to True to mount beetle after moving resources, False to stay dismounted
maxWalkAttempts = 3  # Max number of random walks to find trees before stopping

# Item IDs
logID = 0x1BDD
boardID = 0x1BD7
axeList = [0x0F49, 0x13FB, 0x0F47, 0x1443, 0x0F45, 0x0F4B, 0x0F43]
treeStaticIDs = [
    0x0C95, 0x0C96, 0x0C99, 0x0C9B, 0x0C9C, 0x0C9D, 0x0C8A, 0x0CA6,
    0x0CA8, 0x0CAA, 0x0CAB, 0x0CC3, 0x0CC4, 0x0CC8, 0x0CC9, 0x0CCA,
    0x0CCB, 0x0CCC, 0x0CCD, 0x0CD0, 0x0CD3, 0x0CD6, 0x0CD8, 0x0CDA,
    0x0CDD, 0x0CE0, 0x0CE3, 0x0CE6, 0x0CF8, 0x0CFB, 0x0CFE, 0x0D01,
    0x0D25, 0x0D27, 0x0D35, 0x0D37, 0x0D38, 0x0D42, 0x0D43, 0x0D59,
    0x0D70, 0x0D85, 0x0D94, 0x0D96, 0x0D98, 0x0D9A, 0x0D9C, 0x0D9E,
    0x0DA0, 0x0DA2, 0x0DA4, 0x0DA8,
]

# Adjust tree IDs for UoAlive shard
if Misc.ShardName() == 'UoAlive':
    treeStaticIDsToRemove = [0x0C99, 0x0C9A, 0x0C9B, 0x0C9C, 0x0C9D, 0x0CA6, 0x0CC4]
    for treeStaticIDToRemove in treeStaticIDsToRemove:
        if treeStaticIDToRemove in treeStaticIDs:
            treeStaticIDs.remove(treeStaticIDToRemove)

trees = []
onLoop = True
blockCount = 0
walkAttempts = 0

class Tree:
    def __init__(self, x, y, z, id):
        self.x = x
        self.y = y
        self.z = z
        self.id = id

def say(text):
    spk = SpeechSynthesizer()
    spk.Speak(text)

def WalkRandomDirection():
    global walkAttempts, maxWalkAttempts, onLoop
    directions = [
        (0, -1),  # North
        (1, -1),  # Northeast
        (1, 0),   # East
        (1, 1),   # Southeast
        (0, 1),   # South
        (-1, 1),  # Southwest
        (-1, 0),  # West
        (-1, -1)  # Northwest
    ]
    
    # Select a random direction
    dx, dy = random.choice(directions)
    target_x = Player.Position.X + (dx * 20)
    target_y = Player.Position.Y + (dy * 20)
    
    Misc.SendMessage(f'--> No trees found, walking 10 tiles in direction ({dx}, {dy}) to {target_x}, {target_y}', 77)
    Misc.Resync()
    
    # Set up pathfinding
    route = PathFinding.Route()
    route.MaxRetry = 10
    route.StopIfStuck = False
    route.X = target_x
    route.Y = target_y
    
    # Attempt to move to the target location
    if PathFinding.Go(route):
        Misc.Pause(1000)
        Misc.SendMessage(f'--> Reached position {target_x}, {target_y}', 77)
    else:
        Misc.SendMessage(f'--> Failed to reach {target_x}, {target_y}, trying again later', 33)
    
    walkAttempts += 1
    Misc.SendMessage(f'--> Walk attempt {walkAttempts}/{maxWalkAttempts}', 77)

def MoveToBeetle():
    global packAnimals, logID, boardID, dragDelay, onLoop, mountAfterMove
    
    # Convert logs to boards if specified
    if logsToBoards:
        for item in Player.Backpack.Contains:
            if item.ItemID == logID:
                Items.UseItem(Player.GetItemOnLayer('LeftHand'))
                Target.WaitForTarget(1500, False)
                Target.TargetExecute(item)
                Misc.Pause(dragDelay)

    # Dismount if mounted
    if Player.Mount:
        Mobiles.UseMobile(Player.Serial)
        Misc.Pause(dragDelay)

    # Move logs/boards to beetles
    for item in Player.Backpack.Contains:
        if (logsToBoards and item.ItemID == boardID) or (not logsToBoards and item.ItemID == logID):
            moved = False
            for pack in packAnimals:
                if pack['type'] == 'beetle':
                    beetle_mobile = Mobiles.FindBySerial(pack['serial'])
                    if beetle_mobile:
                        number_in_beetle = GetNumberOfResourcesInBeetle(pack['serial'])
                        Misc.SendMessage(f"Checking beetle {hex(pack['serial'])}: {number_in_beetle}/{beetleWeightLimit} items", 77)
                        if number_in_beetle + item.Amount <= beetleWeightLimit:
                            Items.Move(item.Serial, pack['serial'], 0)
                            Misc.Pause(dragDelay)
                            Misc.SendMessage(f"Moved {item.Amount} items to beetle {hex(pack['serial'])}", 77)
                            moved = True
                            break
            if not moved:
                Misc.SendMessage("No pack beetle with enough space for backpack item!", 33)
                say('All pack beetles are full, stop and unload')
                onLoop = False
                return

    # Check for ground items (logs/boards)
    groundItems = filterItem([boardID, logID], range=2, movable=True)
    for item in groundItems:
        if (logsToBoards and item.ItemID == boardID) or (not logsToBoards and item.ItemID == logID):
            moved = False
            for pack in packAnimals:
                if pack['type'] == 'beetle':
                    beetle_mobile = Mobiles.FindBySerial(pack['serial'])
                    if beetle_mobile:
                        number_in_beetle = GetNumberOfResourcesInBeetle(pack['serial'])
                        Misc.SendMessage(f"Checking beetle {hex(pack['serial'])}: {number_in_beetle}/{beetleWeightLimit} items for ground item", 77)
                        if number_in_beetle + item.Amount <= beetleWeightLimit:
                            Items.Move(item.Serial, pack['serial'], 0)
                            Misc.Pause(dragDelay)
                            Misc.SendMessage(f"Moved {item.Amount} ground items to beetle {hex(pack['serial'])}", 77)
                            moved = True
                            break
            if not moved:
                Misc.SendMessage("No pack beetle with enough space for ground item!", 33)
                say('All pack beetles are full, stop and unload')
                onLoop = False
                return

    # Remount on the nearest beetle if configured
    if mountAfterMove and not Player.Mount:
        nearest_beetle = None
        min_distance = float('inf')
        for pack in packAnimals:
            if pack['type'] == 'beetle':
                beetle_mobile = Mobiles.FindBySerial(pack['serial'])
                if beetle_mobile:
                    distance = sqrt(pow(beetle_mobile.Position.X - Player.Position.X, 2) + 
                                    pow(beetle_mobile.Position.Y - Player.Position.Y, 2))
                    if distance < min_distance:
                        min_distance = distance
                        nearest_beetle = pack['serial']
        if nearest_beetle:
            Misc.SendMessage(f"Mounting beetle {hex(nearest_beetle)}", 77)
            Mobiles.UseMobile(nearest_beetle)
            Misc.Pause(dragDelay)
        else:
            Misc.SendMessage("No beetles available to mount!", 33)
    elif not mountAfterMove and not Player.Mount:
        Misc.SendMessage("mountAfterMove is False, staying dismounted", 77)

def GetNumberOfResourcesInBeetle(beetle_serial):
    beetle_mobile = Mobiles.FindBySerial(beetle_serial)
    if not beetle_mobile:
        Misc.SendMessage(f"Beetle {hex(beetle_serial)} not found!", 33)
        return 0
    
    number = 0
    for item in beetle_mobile.Backpack.Contains:
        if item.ItemID == boardID or item.ItemID == logID:
            number += item.Amount
    return number

def filterItem(id, range=2, movable=True):
    fil = Items.Filter()
    fil.Movable = movable
    fil.RangeMax = range
    graphics_list = List[Int32]()
    for item_id in id:
        graphics_list.Add(item_id)
    fil.Graphics = graphics_list
    return Items.ApplyFilter(fil)

def EquipAxe():
    global axeSerial, onLoop
    leftHand = Player.CheckLayer('LeftHand')
    
    if not leftHand:
        axe_found = False
        for item in Player.Backpack.Contains:
            if item.ItemID in axeList:
                Misc.SendMessage(f'Equipping axe: Serial {hex(item.Serial)}, ID {hex(item.ItemID)}', 77)
                Player.EquipItem(item.Serial)
                Misc.Pause(1000)
                equipped_item = Player.GetItemOnLayer('LeftHand')
                if equipped_item and equipped_item.ItemID in axeList:
                    axeSerial = equipped_item.Serial
                    Misc.SendMessage(f'Axe equipped: Serial {hex(axeSerial)}', 77)
                    axe_found = True
                    return
                else:
                    Misc.SendMessage('Failed to equip axe!', 33)
        if not axe_found:
            axe_item = Items.FindBySerial(axeSerial)
            if axe_item and axe_item.ItemID in axeList and Items.GetPropValue(axe_item, 'Container') == Player.Backpack.Serial:
                Misc.SendMessage(f'Equipping specified axe: Serial {hex(axeSerial)}', 77)
                Player.EquipItem(axeSerial)
                Misc.Pause(1000)
                equipped_item = Player.GetItemOnLayer('LeftHand')
                if equipped_item and equipped_item.ItemID in axeList:
                    axeSerial = equipped_item.Serial
                    Misc.SendMessage(f'Axe equipped: Serial {hex(axeSerial)}', 77)
                    return
                else:
                    Misc.SendMessage('Failed to equip specified axe!', 33)
            Misc.SendMessage('You must have an axe to chop trees! Check backpack and axeSerial.', 33)
            onLoop = False
    elif Player.GetItemOnLayer('LeftHand').ItemID in axeList:
        axeSerial = Player.GetItemOnLayer('LeftHand').Serial
        Misc.SendMessage(f'Axe already equipped: Serial {hex(axeSerial)}', 77)
    else:
        Misc.SendMessage('You must have an axe to chop trees! Non-axe item equipped.', 33)
        onLoop = False

def ScanStatic():
    global trees
    Misc.SendMessage('--> Scan Tile Started', 77)
    minX = Player.Position.X - scanRadius
    maxX = Player.Position.X + scanRadius
    minY = Player.Position.Y - scanRadius
    maxY = Player.Position.Y + scanRadius
    x = minX
    y = minY
    while x <= maxX:
        while y <= maxY:
            staticsTileInfo = Statics.GetStaticsTileInfo(x, y, Player.Map)
            if staticsTileInfo.Count > 0:
                for tile in staticsTileInfo:
                    for staticid in treeStaticIDs:
                        if staticid == tile.StaticID and not Timer.Check('%i,%i' % (x, y)):
                            trees.append(Tree(x, y, tile.StaticZ, tile.StaticID))
            y = y + 1
        y = minY
        x = x + 1
    trees = sorted(trees, key=lambda tree: sqrt(pow((tree.x - Player.Position.X), 2) + pow((tree.y - Player.Position.Y), 2)))
    Misc.SendMessage('--> Total Trees: %i' % len(trees), 77)

def RangeTree():
    playerX = Player.Position.X
    playerY = Player.Position.Y
    treeX = trees[0].x
    treeY = trees[0].y
    return (treeX >= playerX - 1 and treeX <= playerX + 1) and (treeY >= playerY - 1 and treeY <= playerY + 1)

def MoveToTree():
    global trees
    if not trees:
        return
    pathlock = 0
    Misc.SendMessage('--> Moving to TreeSpot: %i, %i' % (trees[0].x, trees[0].y), 77)
    Misc.Resync()
    treeCoords = PathFinding.Route()
    treeCoords.MaxRetry = 10
    treeCoords.StopIfStuck = False
    treeCoords.X = trees[0].x
    treeCoords.Y = trees[0].y + 1
    
    if PathFinding.Go(treeCoords):
        Misc.Pause(1000)
    else:
        Misc.Resync()
        treeCoords.X = trees[0].x + 1
        treeCoords.Y = trees[0].y
        if PathFinding.Go(treeCoords):
            Misc.SendMessage('Second Try')
        else:
            treeCoords.X = trees[0].x - 1
            treeCoords.Y = trees[0].y
            if PathFinding.Go(treeCoords):
                Misc.SendMessage('Third Try')
            else:
                treeCoords.X = trees[0].x
                treeCoords.Y = trees[0].y - 1
                Misc.SendMessage('Final Try')
                if not PathFinding.Go(treeCoords):
                    return
    
    Misc.Resync()
    while not RangeTree():
        Misc.Pause(100)
        pathlock += 1
        if pathlock > 350:
            Misc.Resync()
            treeCoords = PathFinding.Route()
            treeCoords.MaxRetry = 5
            treeCoords.StopIfStuck = False
            treeCoords.X = trees[0].x
            treeCoords.Y = trees[0].y + 1
            if PathFinding.Go(treeCoords):
                Misc.Pause(1000)
            else:
                treeCoords.X = trees[0].x + 1
                treeCoords.Y = trees[0].y
                if PathFinding.Go(treeCoords):
                    Misc.SendMessage('Second Try')
                else:
                    treeCoords.X = trees[0].x - 1
                    treeCoords.Y = trees[0].y
                    if PathFinding.Go(treeCoords):
                        Misc.SendMessage('Third Try')
                    else:
                        treeCoords.X = trees[0].x
                        treeCoords.Y = trees[0].y - 1
                        Misc.SendMessage('Final Try')
                        if not PathFinding.Go(treeCoords):
                            return
            pathlock = 0
    Misc.SendMessage('--> Reached TreeSpot: %i, %i' % (trees[0].x, trees[0].y), 77)

def CutTree():
    global blockCount, trees
    if not trees:
        return
    if Target.HasTarget():
        Misc.SendMessage('--> Detected block, canceling target!', 77)
        Target.Cancel()
        Misc.Pause(500)

    if Player.Weight >= weightLimit:
        MoveToBeetle()
        MoveToTree()

    Journal.Clear()
    Items.UseItem(Player.GetItemOnLayer('LeftHand'))
    Target.WaitForTarget(2000, True)
    Target.TargetExecute(trees[0].x, trees[0].y, trees[0].z, trees[0].id)
    Timer.Create('chopTimer', 10000)
    while not (Journal.SearchByType('You hack at the tree for a while, but fail to produce any useable wood.', 'System') or 
               Journal.SearchByType('You chop some', 'System') or 
               Journal.SearchByType('There\'s not enough wood here to harvest.', 'System') or
               not Timer.Check('chopTimer')):
        Misc.Pause(100)

    if Journal.SearchByType('There\'s not enough wood here to harvest.', 'System'):
        Misc.SendMessage('--> Tree change', 77)
        Timer.Create('%i,%i' % (trees[0].x, trees[0].y), treeCooldown)
    elif Journal.Search('That is too far away'):
        blockCount += 1
        Journal.Clear()
        if blockCount > 3:
            blockCount = 0
            Misc.SendMessage('--> Possible block detected tree change', 77)
            Timer.Create('%i,%i' % (trees[0].x, trees[0].y), treeCooldown)
        else:
            CutTree()
    elif Journal.Search('bloodwood'):
        Player.HeadMessage(1194, 'BLOODWOOD!')
        Timer.Create('chopTimer', 10000)
        CutTree()
    elif Journal.Search('heartwood'):
        Player.HeadMessage(1193, 'HEARTWOOD!')
        Timer.Create('chopTimer', 10000)
        CutTree()
    elif Journal.Search('frostwood'):
        Player.HeadMessage(1151, 'FROSTWOOD!')
        Timer.Create('chopTimer', 10000)
        CutTree()
    elif not Timer.Check('chopTimer'):
        Misc.SendMessage('--> Tree change', 77)
        Timer.Create('%i,%i' % (trees[0].x, trees[0].y), treeCooldown)
    else:
        CutTree()

toonFilter = Mobiles.Filter()
toonFilter.Enabled = True
toonFilter.RangeMin = -1
toonFilter.RangeMax = -1
toonFilter.IsHuman = True 
toonFilter.Friend = False
toonFilter.Notorieties = List[Byte](bytes([1,2,3,4,5,6,7]))

invulFilter = Mobiles.Filter()
invulFilter.Enabled = True
invulFilter.RangeMin = -1
invulFilter.RangeMax = -1
invulFilter.Friend = False
invulFilter.Notorieties = List[Byte](bytes([7]))

def safteyNet():
    if alert:
        toon = Mobiles.ApplyFilter(toonFilter)
        invul = Mobiles.ApplyFilter(invulFilter)
        if toon:
            Misc.FocusUOWindow()
            say("Hey, someone is here. You should tab over and take a look At The Screen")
            toonName = Mobiles.Select(toon, 'Nearest')
            if toonName:
                Misc.SendMessage('Toon Near: ' + toonName.Name, 33)
        elif invul:
            say("Hey, something invulnerable here. You should tab over and take a look")
            invulName = Mobiles.Select(invul, 'Nearest')
            if invulName:
                Misc.SendMessage('ALERT: Invul! Who the Hell is ' + invulName.Name, 33)
        else:
            Misc.NoOperation()

# Main execution block
Friend.ChangeList('lj')
Misc.SendMessage('--> Starting Lumberjacking', 77)

if onLoop:
    EquipAxe()
    while onLoop:
        ScanStatic()
        while trees:
            safteyNet()
            EquipAxe()
            MoveToTree()
            CutTree()
            trees.pop(0)
            trees = sorted(trees, key=lambda tree: sqrt(pow((tree.x - Player.Position.X), 2) + pow((tree.y - Player.Position.Y), 2)))
        trees = []
        
        # Walk 20 tiles in a random direction to find more trees
        if walkAttempts < maxWalkAttempts:
            WalkRandomDirection()
        else:
            Misc.SendMessage('--> No trees found after max walk attempts, stopping script. Move to a new location and restart.', 33)
            onLoop = True
            break
    Misc.Pause(100)