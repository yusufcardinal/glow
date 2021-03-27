"""
Glow.py v0.1 Public Release

Creator: Mile
Huge thanks to FerrariFlunker, Bytebit and BR for their invaluable help!

COPY THIS TO YOUR map.txt FILE FOR MAP-SPECIFIC CONTROL AND ENABLE GLOW ON THE MAP

extensions = {
    'glow_enabled': True,
    'glow_stored_colors': {}
}

"""

import math
import random
from twisted.internet.reactor import addSystemEventTrigger, callLater
from pyspades.contained import BlockAction, SetColor
from pyspades.constants import *
from pyspades.common import make_color
from piqueserver.commands import command, get_player, name, admin

# USER INPUTS

# ANTI LAG LINE
# Creating lines of light blocks may cause a lot of server-side lag, especially with a full server. ANTI_LAG_LIMIT is
# the maximum amount of blocks that can light up in a line when ANTI_LAG_LINE is on. Change ANTI_LAG_LINE to False to
# turn off. Players in god mode can place as many light blocks as they want at once, regardless of these settings.

ANTI_LAG_LINE = True
ANTI_LAG_LIMIT = 5

# PALETTE TOGGLE
# This turns off colors from the color palette so they may not glow. The script makes it so about half the color palette
# glows by default, this reduces the number of glowy blocks to the three lightest columns of player palette.

PALETTE_TOGGLE = True
PALETTE_PLAYER = list([(255, 31, 31), (255, 143, 31), (255, 255, 31), (31, 255, 31), (31, 255, 255), (31, 31, 255), (255, 31, 255)])

# TOGGLE STORED_COLORS RECORDING
# Toggles if STORED_COLORS gets dumped to a file on server shutdown. If you wish for your map to have glow blocks on it,
# you will need to dump STORED_COLORS and append the values to your map's extensions (glow_stored_colors). You can
# refer to the example maps if you're unsure how to proceed. Can also be toggled on in-game by an admin with the use of
# "/glowrecord".

GLOW_RECORDING = False

# ALWAYS_GLOW
# Forces glow to run on all maps. Unintended behavior may arise

ALWAYS_GLOW = False

# END OF USER INPUTS

MAP_IS_GLOW = False

DISABLED_USERS_GLOW = []

with open('img/userdata/DISABLED_USERS_GLOW.txt', 'r') as userd:
    for name in userd:
        DISABLED_USERS_GLOW.append(name.rstrip('\n'))

# Pool where voxels are processed
VOXEL_PROC_GLOW = {}

# Colors saved from the map.
STORED_COLORS = {}


def empty_lights(a, b, c, map, is_palette):
    re, ge, be = map.get_color(a, b, c)
    if is_palette:
        sub = 1
    else:
        sub = 25
    add = tuple((a, b, c))
    VOXEL_PROC_GLOW[add] = tuple((re-sub, ge-sub, be-sub))
    if add not in STORED_COLORS:
        STORED_COLORS[add] = tuple((re-sub, ge-sub, be-sub))


def glownupon_block_user(a, b, c, value, tolerance, map, color):

    R1, G1, B1 = color
    add = tuple((a, b, c))
    voxel_selection_user = list()
    toleranceVal = 2

    for a2 in range(a-value, a+value):
        for b2 in range(b-value, b+value):
            for c2 in range(c-value, c+value):
                chk = tuple((a2, b2, c2))
                if chk in STORED_COLORS and 255 in STORED_COLORS[chk]:
                    if map.get_solid(a2, b2, c2):
                        toleranceVal += 1
                        voxel_selection_user.append(chk)

    if len(voxel_selection_user) == 0:
        return

    for p in voxel_selection_user:
        R2, G2, B2 = map.get_color(p[0], p[1], p[2])
        distance = math.sqrt((p[0] - a) ** 2 + (p[1] - b) ** 2 + (p[2] - c) ** 2)
        if distance > value:
            continue
        else:
            if add in VOXEL_PROC_GLOW:
                R1 = VOXEL_PROC_GLOW[add][0] + int((R2 - (distance / value) * R2) / toleranceVal-1)
                G1 = VOXEL_PROC_GLOW[add][1] + int((G2 - (distance / value) * G2) / toleranceVal-1)
                B1 = VOXEL_PROC_GLOW[add][2] + int((B2 - (distance / value) * B2) / toleranceVal-1)
            else:
                R1 = R1 + int((R2 - (distance / value) * R2) / toleranceVal-1)
                G1 = G1 + int((G2 - (distance / value) * G2) / toleranceVal-1)
                B1 = B1 + int((B2 - (distance / value) * B2) / toleranceVal-1)
            if R1 > 254:
                R1 = 254
            if G1 > 254:
                G1 = 254
            if B1 > 254:
                B1 = 254
            if R1 < 0:
                R1 = 0
            if G1 < 0:
                G1 = 0
            if B1 < 0:
                B1 = 0
            if add in STORED_COLORS and 255 in STORED_COLORS[add]:
                    R1 = STORED_COLORS[add][0]
                    G1 = STORED_COLORS[add][1]
                    B1 = STORED_COLORS[add][2]
            VOXEL_PROC_GLOW[add] = tuple((R1, G1, B1))


def glow_block_user(protocol, a, b, c, value, tolerance, map):

    R1, G1, B1 = map.get_color(a, b, c)
    voxel_selection_user = list()
    toleranceVal = 2.
    preProcNumber = len(VOXEL_PROC_GLOW)

    for ac in range(a-tolerance, a+tolerance):
        for bc in range(b-tolerance, b+tolerance):
            for cc in range(c-tolerance, c+tolerance):
                chk = tuple((ac, bc, cc))
                if chk in STORED_COLORS and 255 in STORED_COLORS[chk]:
                        toleranceVal += 1


    for a2 in range(a-value, a+value):
        for b2 in range(b-value, b+value):
            for c2 in range(c-value, c+value):
                if map.get_solid(a2, b2, c2):
                    result = tuple((a2, b2, c2))
                    voxel_selection_user.append(result)

    for p in voxel_selection_user:
        R2, G2, B2 = map.get_color(p[0], p[1], p[2])
        distance = math.sqrt((p[0] - a) ** 2 + (p[1] - b) ** 2 + (p[2] - c) ** 2)
        if distance > value:
            continue
        if R2 == 0 and G2 == 0 and B2 == 0:
            continue
        else:
            if p not in STORED_COLORS:
                STORED_COLORS[p] = tuple((R2, G2, B2))
            value = float(value)
            R1, G1, B1, R2, G2, B2 = float(R1), float(G1), float(B1), float(R2), float(G2), float(B2)
            if p in VOXEL_PROC_GLOW:
                R3 = int(VOXEL_PROC_GLOW[p][0] + (R1 - (distance / value) * R1) / toleranceVal-1)
                G3 = int(VOXEL_PROC_GLOW[p][1] + (G1 - (distance / value) * G1) / toleranceVal-1)
                B3 = int(VOXEL_PROC_GLOW[p][2] + (B1 - (distance / value) * B1) / toleranceVal-1)
            else:
                R3 = int(R2 + (R1 - (distance / value) * R1) / toleranceVal-1)
                G3 = int(G2 + (G1 - (distance / value) * G1) / toleranceVal-1)
                B3 = int(B2 + (B1 - (distance / value) * B1) / toleranceVal-1)
            if R3 > 254:
                R3 = 254
            if G3 > 254:
                G3 = 254
            if B3 > 254:
                B3 = 254
            if R3 < 0:
                R3 = 0
            if G3 < 0:
                G3 = 0
            if B3 < 0:
                B3 = 0
            if 255 not in map.get_color(p[0], p[1], p[2]):
                VOXEL_PROC_GLOW[p] = tuple((R3, G3, B3))
    postProcNumber = len(VOXEL_PROC_GLOW)
    countType = postProcNumber - preProcNumber
    trigger(protocol, map, countType)


def unglow_block_user(protocol, a, b, c, value, tolerance, map):

    R1, G1, B1 = map.get_color(a, b, c)
    voxel_selection_user = list()
    toleranceVal = 2
    preProcNumber = len(VOXEL_PROC_GLOW)
    for ac in range(a-tolerance, a+tolerance):
        for bc in range(b-tolerance, b+tolerance):
            for cc in range(c-tolerance, c+tolerance):
                chk = tuple((ac, bc, cc))
                if chk in STORED_COLORS and 255 in STORED_COLORS[chk]:
                        toleranceVal += 1

    for a2 in range(a-value, a+value):
        for b2 in range(b-value, b+value):
            for c2 in range(c-value, c+value):
                if map.get_solid(a2, b2, c2):
                    result = tuple((a2, b2, c2))
                    voxel_selection_user.append(result)
    for p in voxel_selection_user:
        R2, G2, B2 = map.get_color(p[0], p[1], p[2])
        distance = math.sqrt((p[0] - a) ** 2 + (p[1] - b) ** 2 + (p[2] - c) ** 2)
        if distance > value:
            continue
        if R2 == 0 and G2 == 0 and B2 == 0:
            continue
        else:
            value = float(value)
            R1, G1, B1, R2, G2, B2 = float(R1), float(G1), float(B1), float(R2), float(G2), float(B2)
            if p in VOXEL_PROC_GLOW:
                R3 = int(VOXEL_PROC_GLOW[p][0] - (R1 - (distance/value)*R1)/toleranceVal-1)
                G3 = int(VOXEL_PROC_GLOW[p][1] - (G1 - (distance/value)*G1)/toleranceVal-1)
                B3 = int(VOXEL_PROC_GLOW[p][2] - (B1 - (distance/value)*B1)/toleranceVal-1)
            else:
                R3 = int(R2 - (R1 -(distance/value)*R1)/toleranceVal - 1)
                G3 = int(G2 - (G1 -(distance/value)*G1)/toleranceVal - 1)
                B3 = int(B2 - (B1 -(distance/value)*B1)/toleranceVal - 1)
            if R3 > 254:
                R3 = 254
            if G3 > 254:
                G3 = 254
            if B3 > 254:
                B3 = 254
            if R3 < 0:
                R3 = 0
            if G3 < 0:
                G3 = 0
            if B3 < 0:
                B3 = 0
        if p in STORED_COLORS:
            if R3 < STORED_COLORS[p][0]:
                R3 = STORED_COLORS[p][0]
            if G3 < STORED_COLORS[p][1]:
                G3 = STORED_COLORS[p][1]
            if B3 < STORED_COLORS[p][2]:
                B3 = STORED_COLORS[p][2]
            if 255 not in map.get_color(p[0], p[1], p[2]):
                VOXEL_PROC_GLOW[p] = tuple((R3, G3, B3))
    postProcNumber = len(VOXEL_PROC_GLOW)
    countType = postProcNumber - preProcNumber
    trigger(protocol, map, countType)


def processvoxels(protocol, map):
    entry_list = list(VOXEL_PROC_GLOW.items())
    randomVox = random.choice(entry_list)
    VOXEL_PROC_GLOW.pop(randomVox[0])
    p = randomVox[0]
    RGB = randomVox[1]
    if map.get_solid(p[0], p[1], p[2]):
        block_action, set_color = BlockAction(), SetColor()
        set_color.value = make_color(RGB[0], RGB[1], RGB[2])
        set_color.player_id = 33
        protocol.broadcast_contained(set_color)
        block_action.player_id = 33
        map.set_point(p[0], p[1], p[2], RGB)
        block_action.x = p[0]
        block_action.y = p[1]
        block_action.z = p[2]
        block_action.value = BUILD_BLOCK
        # Send block updates to everyone but voxlap and turned off users
        protocol.broadcast_contained(block_action, save=True, rule=lambda p: p.is_glow is True)
    else:
        return


def client_check(self):
    goodclient = ["OpenSpades", "BetterSpades"]
    for client in goodclient:
        if not self.is_glow and client in self.client_string and self.name not in DISABLED_USERS_GLOW:
            self.is_glow = True
            self.send_chat("Client authentication complete. Glow turned ON.")


def trigger(protocol, map, countType):
    iter = 0.0
    count = 0
    while count < countType:
        callLater(iter, processvoxels, protocol, map)
        iter += 0.005
        count += 1


@command('glow')
def off_glow(self):
    if "Voxlap" not in self.client_string:
        if self.is_glow:
            self.is_glow = False
            if self.name not in DISABLED_USERS_GLOW:
                DISABLED_USERS_GLOW.append(self.name)
            self.send_chat("Glow turned OFF. Name added to OFF registry.")
        else:
            self.is_glow = True
            if self.name in DISABLED_USERS_GLOW:
                DISABLED_USERS_GLOW.remove(self.name)
            self.send_chat("Glow turned ON. Name removed from OFF registry.")
    else:
        self.send_chat("Cannot run glow on classic client. Please upgrade to OpenSpades or BetterSpades.")


@command('glowmap')
def glowmap(self):
    global MAP_IS_GLOW
    if self.user_types.moderator or self.admin:
        if MAP_IS_GLOW:
            MAP_IS_GLOW = False
            self.send_chat("Glow turned OFF globally.")
        else:
            MAP_IS_GLOW = True
            self.send_chat("Glow turned ON globally.")
    else:
        self.send_chat("Permission denied.")


@command('glowrecord')
def glowrecord(self):
    global GLOW_RECORDING
    if self.admin:
        if GLOW_RECORDING:
            GLOW_RECORDING = False
            self.send_chat("Glow record OFF. STORED_COLORS will not be dumped on system shutdown.")
        else:
            GLOW_RECORDING = True
            self.send_chat("Glow record ON. STORED_COLORS will be dumped on system shutdown.")
    else:
        self.send_chat("Permission denied.")


def apply_script(protocol, connection, config):

    class GlowProtocol(protocol):
        def __init__(self, *arg, **kw):
            protocol.__init__(self, *arg, **kw)
            addSystemEventTrigger('before', 'shutdown', self.save_storedcolor)

        def save_storedcolor(self):
            if GLOW_RECORDING:
                with open('STORED_COLOR.txt', 'w') as file:
                    file.write(str(STORED_COLORS))
            else:
                return

        def on_map_change(self, map):
            global ALWAYS_GLOW, MAP_IS_GLOW, STORED_COLORS, VOXEL_PROC_GLOW, GLOW_RECORDING
            extensions = self.map_info.extensions
            VOXEL_PROC_GLOW.clear()
            GLOW_RECORDING = False
            if 'glow_enabled' in extensions:
                MAP_IS_GLOW = extensions['glow_enabled']
            elif ALWAYS_GLOW:
                MAP_IS_GLOW = True
            else:
                MAP_IS_GLOW = False
            if 'glow_stored_colors' in extensions:
                STORED_COLORS = extensions['glow_stored_colors']
            else:
                STORED_COLORS.clear()
            with open('img/userdata/DISABLED_USERS_GLOW.txt', 'w') as file:
                userstr = ""
                for user in DISABLED_USERS_GLOW:
                    userstr += str(user) + "\n"
                file.write(userstr)
            return protocol.on_map_change(self, map)

    class GlowConnection(connection):

        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.is_glow = False

        def on_spawn(self, pos):
            callLater(5.5, client_check, self)
            return connection.on_spawn(self, pos)

        def on_block_build(self, a, b, c):
            if MAP_IS_GLOW:
                map = self.protocol.map
                protocol = self.protocol
                color = map.get_color(a, b, c)
                p2 = tuple((a, b, c))
                if PALETTE_TOGGLE and color in PALETTE_PLAYER:
                    return connection.on_block_build(self, a, b, c)
                else:
                    if 255 in color:
                        STORED_COLORS[p2] = color
                        glow_block_user(protocol, a, b, c, 7, 5, map)

                        return connection.on_block_build(self, a, b, c)
                    else:
                        STORED_COLORS[p2] = color
                        preProcNumber = len(VOXEL_PROC_GLOW)
                        glownupon_block_user(a, b, c, 7, 5, map, color)
                        postProcNumber = len(VOXEL_PROC_GLOW)
                        countType = postProcNumber - preProcNumber
                        trigger(protocol, map, countType)

                        return connection.on_block_build(self, a, b, c)
            else:
                #Map isn't glow enabled
                return connection.on_block_build(self, a, b, c)

            return connection.on_block_build(self, a, b, c)

        def on_block_destroy(self, a, b, c, mode):
            if MAP_IS_GLOW:
                map = self.protocol.map
                protocol = self.protocol
                color = map.get_color(a, b, c)
                p2 = tuple((a, b, c))
                if p2 in STORED_COLORS:
                    del STORED_COLORS[p2]
                if PALETTE_TOGGLE and color in PALETTE_PLAYER:
                    return connection.on_block_destroy(self, a, b, c, mode)
                else:
                    if mode != GRENADE_DESTROY:
                        if 255 in color:
                            unglow_block_user(protocol, a, b, c, 7, 5, map)
            else:
                #Map isn't glow enabled
                return connection.on_block_destroy(self, a, b, c, mode)
            return connection.on_block_destroy(self, a, b, c, mode)

        def on_line_build(self, points):

            if MAP_IS_GLOW:
                map = self.protocol.map
                protocol = self.protocol
                color = map.get_color(points[0][0], points[0][1], points[0][2])
                if PALETTE_TOGGLE and color in PALETTE_PLAYER:
                    return connection.on_line_build(self, points)
                else:
                    if len(points) > ANTI_LAG_LIMIT and ANTI_LAG_LINE is True and not self.god:
                        if 255 in color:
                            for a, b, c in points:
                                empty_lights(a, b, c, map, 0)
                            countType = len(points)
                            trigger(protocol, map, countType)

                            return connection.on_line_build(self, points)
                        else:
                            preProcNumber = len(VOXEL_PROC_GLOW)
                            for a, b, c in points:
                                p2 = tuple((a, b, c))
                                glownupon_block_user(a, b, c, 7, 5, map, color)
                                if p2 not in STORED_COLORS:
                                    STORED_COLORS[p2] = color
                            postProcNumber = len(VOXEL_PROC_GLOW)
                            countType = postProcNumber - preProcNumber
                            trigger(protocol, map, countType)

                            return connection.on_line_build(self, points)
                    else:
                        if 255 in color:
                            for a, b, c in points:
                                glow_block_user(protocol, a, b, c, 7, 5, map)
                                p2 = tuple((a, b, c))
                                if p2 not in STORED_COLORS:
                                    STORED_COLORS[p2] = color

                                return connection.on_line_build(self, points)
                        else:
                            preProcNumber = len(VOXEL_PROC_GLOW)
                            for a, b, c in points:
                                p2 = tuple((a, b, c))
                                glownupon_block_user(a, b, c, 7, 5, map, color)
                                if p2 not in STORED_COLORS:
                                    STORED_COLORS[p2] = color
                            postProcNumber = len(VOXEL_PROC_GLOW)
                            countType = postProcNumber - preProcNumber
                            trigger(protocol, map, countType)

                            return connection.on_line_build(self, points)
            else:
                # Map isn't glow enabled
                return connection.on_line_build(self, points)

            return connection.on_line_build(self, points)

    return GlowProtocol, GlowConnection
