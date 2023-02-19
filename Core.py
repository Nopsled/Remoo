# <!-- SERVER LIST -->
# <script src = "/serverData.js" > </script >

#!/usr/bin/env python

import asyncio
import base64
from hashlib import sha1
import random
import re
import socket
import string
import struct
from threading import Thread
import time
import msgpack
import threading
from Net import PacketCodes




OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xA
class WebSocketFrame:
    def __init__(self, fin=1, opcode=OPCODE_BINARY, payload=b'', mask=None):
        self.fin = fin
        self.opcode = opcode
        self.payload = payload
        self.mask = mask

    def build(self):
        # First byte
        byte1 = 0
        byte1 |= (self.fin << 7)
        byte1 |= self.opcode

        # Second byte
        byte2 = 0
        if self.mask:
            byte2 |= 1 << 7
        payload_length = len(self.payload)
        if payload_length <= 125:
            byte2 |= payload_length
            header = struct.pack('!BB', byte1, byte2)
        elif payload_length <= 0xFFFF:
            byte2 |= 126
            header = struct.pack('!BBH', byte1, byte2, payload_length)
        else:
            byte2 |= 127
            header = struct.pack('!BBQ', byte1, byte2, payload_length)

        # Masking key
        if self.mask:
            masking_key = struct.pack('!I', self.mask)
            header += masking_key

        # Payload data
        if self.mask:
            masked_payload = bytearray(self.payload)
            for i in range(payload_length):
                masked_payload[i] ^= masking_key[i % 4]
            return header + masked_payload
        else:
            return header + self.payload



#class PredefinedPackets:
 #   PACKET = ["9", [resource('wood'), amount(100), playerid(0)]]

class GameWorldManager:
    instances = []
    
    def broadcastWorldCommand():
        pass
    
    # resource = ["wood", "stone"]
    def setResourceForAllPlayers(resource="stone", amount=100):
        for client in GameWorldManager.instances:
            client.playerObject.setResource(resource, amount)
            
    def getAllPlayers():
        pass
    
    def sendChatMessage():
        pass
            

            

class GameObject:
    def __init__(self, id=random.randint(0, 999), x=random.randint(0, 300), y=random.randint(0, 300), scale=random.randint(10,100), type=random.randint(0,3)):
        
        self.id = id # (always unique int like 100-999)
        self.x = 250
        self.y = 250
        self.unk1 = 0  # Validate
        self.scale = scale  # Size: 0-?
        self.type = type  # (Interval: 0-3, design or function?)
        self.unk4 = None  # Validate (None / Null)
        self.unk5 = -1  # Validate (-1)
        
    def __repr__(self):
        return f"{self.id},\n{self.x},\n{self.y},\n{self.unk1},\n{self.scale},\n{self.type},\n{self.unk4},\n{self.unk5}"
    
    def get(self):
        return [self.id, self.x, self.y, self.unk1, self.scale, self.type, self.unk4, self.unk5]



class PlayerObject:
    def __init__(self, socket, id=1, y=0, x=0, angle=0.0, usingItemID=1, unk2=0, unk3=0, unk4=None, clanLeader=0, skin=0, usingAccessoryID=0, showSkull=0, unk9=0):
        self.socket = socket
        self.id = id
        self.uniqueID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.x = 200
        self.y = 200
        self.angle = 0
        self.usingItemID = -1 # Holding item id (-1 - 3 : -1=Weapon,0=Apple,1=Cookie,2=?,3=Wood,4=Stone,5=BlackStone,6=Trap...)
        self.unk2 = 0 # ?
        self.unk3 = 0 # ?
        self.unk4 = None # ?
        self.clanLeader = clanLeader # Clan leader (symbol)
        self.skin = skin # Character skin ID ()
        self.usingAccessoryID = usingAccessoryID
        self.showSkull = showSkull #Show skull and bones
        self.unk9 = 1
        
        self.name = "unknown"
        self.moofoll = None
        
        self.IS_ATTACKING = 0
        self.IS_MOVING = 0
        self.MOVE_SPEED = 25
        self.MOVE_DIRECTION = "UP" # UP, DOWN, RIGHT, LEFT,   UPLEFT, UPRIGHT, DOWNLEFT, DOWNRIGHT
        
        self.wood = 0
        self.food = 0
        self.stone = 0
        
        #self.movePacket = msgpack.packb(
        #    [1, self.x, self.y, self.angle, -1, 0, 0, None, 0, 0, 0, 0, 0])
        
    def setResource(self, resourceType="wood", amount=10):
        self.wood = amount
        data = ["9", [resourceType, amount, self.id]]
        packet = msgpack.packb(data)
        packet = WebSocketFrame(payload=packet).build()
        self.socket.send(packet)
        print(f'[SEND - ADD_RESOURCE – {self.playerObject.name}]: {data}')
            
            
        
    def __repr__(self):
        pass
    
    def get(self):
        return [self.id, self.x, self.y, self.angle, self.usingItemID, self.unk2, self.unk3, self.unk4, self.clanLeader, self.skin, self.usingAccessoryID, self.showSkull, self.unk9]
        





class GameClient:
    def __init__(self, socket):
        self.socket = socket
        self.socketHandshaked = False
        self.websocket_answer = (
            'HTTP/1.1 101 Switching Protocols',
            'Upgrade: websocket',
            'Connection: Upgrade',
            'Sec-WebSocket-Accept: {key}\r\n\r\n',
        )

        self.playerObject = PlayerObject(self.socket)
        



    def decodeRecieveString(self, stringStreamIn):
        byteArray = stringStreamIn
        datalength = byteArray[1] & 127
        indexFirstMask = 2
        if datalength == 126:
            indexFirstMask = 4
        elif datalength == 127:
            indexFirstMask = 10
        masks = [m for m in byteArray[indexFirstMask: indexFirstMask+4]]
        indexFirstDataByte = indexFirstMask + 4
        decodedChars = []
        i = indexFirstDataByte
        j = 0
        while i < len(byteArray):
            decodedChars.append(chr(byteArray[i] ^ masks[j % 4]))
            i += 1
            j += 1
        return ''.join(decodedChars)
    def decodeRecieveHexArray(self, stringStreamIn):
            byteArray = stringStreamIn
            datalength = byteArray[1] & 127
            indexFirstMask = 2
            if datalength == 126:
                indexFirstMask = 4
            elif datalength == 127:
                indexFirstMask = 10
            masks = [m for m in byteArray[indexFirstMask: indexFirstMask+4]]
            indexFirstDataByte = indexFirstMask + 4
            decodedChars = []
            i = indexFirstDataByte
            j = 0
            while i < len(byteArray):
                byteHex = (byteArray[i] ^ masks[j % 4])
                decodedChars.append(byteHex)
                i += 1
                j += 1
            ret = bytes(decodedChars)
            return ret


    # Update player movement (33 and AI)
    def gameLoop(self):
        while True:
            time.sleep(0.1)
            
            if self.playerObject.IS_MOVING:
                if self.playerObject.MOVE_DIRECTION == "UP":
                    self.playerObject.y += self.playerObject.MOVE_SPEED
                elif self.playerObject.MOVE_DIRECTION == "DOWN":
                    self.playerObject.y -= self.playerObject.MOVE_SPEED
                elif self.playerObject.MOVE_DIRECTION == "RIGHT":
                    self.playerObject.x += self.playerObject.MOVE_SPEED
                elif self.playerObject.MOVE_DIRECTION == "LEFT":
                    self.playerObject.x -= self.playerObject.MOVE_SPEED
                elif self.playerObject.MOVE_DIRECTION == "UPLEFT":
                    self.playerObject.x -= self.playerObject.MOVE_SPEED
                    self.playerObject.y -= self.playerObject.MOVE_SPEED
                elif self.playerObject.MOVE_DIRECTION == "UPRIGHT":
                    self.playerObject.x += self.playerObject.MOVE_SPEED
                    self.playerObject.y -= self.playerObject.MOVE_SPEED
                elif self.playerObject.MOVE_DIRECTION == "DOWNLEFT":
                    self.playerObject.x -= self.playerObject.MOVE_SPEED
                    self.playerObject.y += self.playerObject.MOVE_SPEED
                elif self.playerObject.MOVE_DIRECTION == "DOWNRIGHT":
                    self.playerObject.x += self.playerObject.MOVE_SPEED
                    self.playerObject.y += self.playerObject.MOVE_SPEED
            
            # Update player position and information to client(s).  
            data = ["33", [self.playerObject.get()]]
            packet = msgpack.packb(data)
            packet = WebSocketFrame(payload=packet).build()
            self.socket.send(packet)
            #print(
            #f'[SEND – {self.playerObject.name}:{packetID}]: {data}')



    def recv(self):
        while True:
            data = self.socket.recv(1024)
                                           
            if len(data) > 0:
                
                

                if self.socketHandshaked == False:
                    # Establish the handshake to websocket
                    try:
                        data = data.decode("utf-8")
                        #print("Data decoded: " + data)
                        if "Connection: Upgrade" in data:
                            
                            key = re.search("Sec-WebSocket-Key: (.*?)\r\n", data).group(1)
                            combined = key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                            hash = sha1(combined.encode())
                            b64 = base64.b64encode(hash.digest())
                            response_key = b64.decode("utf-8")
                            response = '\r\n'.join(self.websocket_answer).format(key=response_key)
                        
                            #print("[New game client]: Key found: " + str(key))
                            #print("[New game client]: Response key: " + str(response_key))
                            #print("Response: " + str(response))
                            
                            self.socket.send(response.encode())
                            self.socketHandshaked = True
                    except:
                        print("Not utf-8")
                else:
            
                    try:
                        decodedData = self.decodeRecieveHexArray(data)
                        try:
                            unpackedData = msgpack.unpackb(decodedData)
                            packetHeader = unpackedData[0]
                            packetBody = unpackedData[1]
                            
                            
                            #print("Raw data: " + str(data))
                            #print("Decoded: " + str(decodedData))
                            #print("Unpacked: " + str(unpackedData))                        
                            
                            for packetID, value in PacketCodes.CLIENT.items():
                                if value == packetHeader:
                                    
                                    if packetID != "PING" and packetID != "ANGLE":
                                        print(
                                            f"[{self.playerObject.name}:{packetID}]: {str(unpackedData)}")
                                        
                                    if packetID == "ANGLE":
                                        self.playerObject.angle = float(packetBody[0])
                                    elif packetID == "CHAT":
                                        message = packetBody[0]
                                    elif packetID == "PING":
                                        packet = msgpack.packb(["pp", []])
                                        data = WebSocketFrame(payload=packet).build()
                                        self.socket.send(data)
                                    elif packetID == "GATHER_ANIM":
                                        # Damage packet by client when attacked by player: "7",[1,0,3]
                                        print(f"[{self.playerObject.name}:{packetID}]: {str(unpackedData)}")
                                    elif packetID == "ITEM_BUY":
                                        #[kokoko:ITEM_BUY]: ['13c', [0, 51, 0]]
                                        #self.playerObject.items.add(51)
                                        unk0 = packetBody[0]
                                        hatID = packetBody[1]
                                        unk1 = packetBody[2]
                                        # us = UPDATE_STORE_ITEMS
                                        packet = msgpack.packb(['us', [unk0, hatID, unk1]])
                                        data = WebSocketFrame(payload=packet).build()
                                        self.socket.send(data)
                                    elif packetID == "SELECT_ITEM":
                                        data = ['5', [3, True]]
                                        packet = msgpack.packb(data)
                                        data = WebSocketFrame(payload=packet).build()
                                        self.socket.send(data)
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: {data}')
                                    elif packetID == "MOVE":   

                                        if packetBody[0] != None:
                                            self.playerObject.IS_MOVING = True
                                            if packetBody[0] == 1.57:
                                                self.playerObject.MOVE_DIRECTION = "UP"
                                            elif packetBody[0] == -1.57:
                                                self.playerObject.MOVE_DIRECTION = "DOWN"
                                            elif packetBody[0] == 0:
                                                self.playerObject.MOVE_DIRECTION = "RIGHT"
                                            elif packetBody[0] == 3.14:
                                                self.playerObject.MOVE_DIRECTION = "LEFT"
                                            elif packetBody[0] == -2.36:
                                                self.playerObject.MOVE_DIRECTION = "UPLEFT"
                                            elif packetBody[0] == -0.79:
                                                self.playerObject.MOVE_DIRECTION = "UPRIGHT"
                                            elif packetBody[0] == 2.36:
                                                self.playerObject.MOVE_DIRECTION = "DOWNLEFT"
                                            elif packetBody[0] == 0.79:
                                                self.playerObject.MOVE_DIRECTION = "DOWNRIGHT"
                                        else:
                                            self.playerObject.IS_MOVING = False

                                    elif packetID == "ATTACK":
                                        self.playerObject.IS_ATTACKING = packetBody[0]
                                        data = ["7", [self.playerObject.IS_ATTACKING, 1, 1]]
                                        packet = msgpack.packb(data)
                                        packet = WebSocketFrame(payload=packet).build()
                                        self.socket.send(packet)
                                        # print(f'[{self.playerObject.name}:{packetID}]: {str(packetBody[0])}')
                                    elif packetID == "START":
                                        packetBody = packetBody[0]
                                        self.playerObject.name = packetBody['name']
                                        self.playerObject.moofoll = packetBody['moofoll']
                                        self.playerObject.skin = packetBody['skin']
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: ...')
                                        

                                        # PLAYER_SET_ID [S > C]
                                        data = ["1", [len(GameWorldManager.instances)]]
                                        packet = msgpack.packb(data)
                                        packet = WebSocketFrame(payload=packet).build()
                                        self.socket.send(packet)
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: {data}')


                                        # PLAYER_ADD [S > C]
                                        data = [
                                            "2",
                                            [
                                                [
                                                    self.playerObject.uniqueID,  # Unique string ike "WNTYIDilNF"
                                                    1, # Unk (1 or 2 ?)
                                                    self.playerObject.name,
                                                    self.playerObject.x,
                                                    self.playerObject.y,
                                                    0,  # Unk
                                                    100,  # Unk
                                                    100,  # Unk
                                                    35, # Scale of character
                                                    0 # Skin of character
                                                ],
                                                1
                                            ]
                                        ]
                                        packet = msgpack.packb(data)
                                        packet = WebSocketFrame(payload=packet).build()
                                        self.socket.send(packet)
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: {data}')

                                        # MOVE [S > C]
                                        data = ['33', []]
                                        packet = msgpack.packb(data)
                                        packet = WebSocketFrame(
                                            payload=packet).build()
                                        self.socket.send(packet)
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: {data}')
                 
                                        # "AI_UPDATE": "a"
                                        data = ['a', []]
                                        packet = msgpack.packb(data)
                                        packet = WebSocketFrame(payload=packet).build()
                                        self.socket.send(packet)
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: {data}')

                                        # "LOAD_GAME_OBJ": "6"
                                        # Make 10 game objects
                                        gameObjects = []
                                        for i in range(10):
                                            gameObject = GameObject().get()
                                            gameObjects.extend(gameObject)
                                        
                                        print(str(gameObjects))
                                        
                                            
                                            
                                        data = ["6",[gameObjects]]
                                        packet = msgpack.packb(data)
                                        packet = WebSocketFrame(payload=packet).build()
                                        self.socket.send(packet)
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: {data}')

                                        # "MINIMAP_LOCATIONS": "mm"
                                        data = ["mm",[1]]
                                        packet = msgpack.packb(data)
                                        packet = WebSocketFrame(payload=packet).build()
                                        self.socket.send(packet)
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: {data}')

                                        # "LEADERBOAD": "5"
                                        data = ["5",
                                                [
                                                    [
                                                        1, #Server unique ID
                                                        self.playerObject.name, # Player name
                                                        100 # Score
                                                    ]
                                                ]
                                                ]
                                        packet = msgpack.packb(data)
                                        packet = WebSocketFrame(payload=packet).build()
                                        self.socket.send(packet)
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: {data}')

                           
                                            
                                        # Loop AI_UPDATE[a] + PLAYER_UPDATE[33]
                                        data = ["33",[self.playerObject.get()]]
                                        packet = msgpack.packb(data)
                                        packet = WebSocketFrame(payload=packet).build()
                                        self.socket.send(packet)
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: {data}')

                                        data = ["a",[]]
                                        packet = msgpack.packb(data)
                                        packet = WebSocketFrame(payload=packet).build()
                                        self.socket.send(packet)
                                        print(
                                            f'[SEND – {self.playerObject.name}:{packetID}]: {data}')

                        except Exception as err:
                            print("Exception unpackb: " + str(err))
                        
                    except Exception as err:
                        print("decodeRecieveHexArray error: " + str(err))
    
        self.socket.close()
                    
                    





def on_new_client(clientSocket, clientAddress):
    client = GameClient(clientSocket)
    GameWorldManager.instances.append(client)
    Thread(target=client.recv).start()
    Thread(target=client.gameLoop).start()
    print(f'[+]: New game client connected: {clientAddress}')


if __name__ == "__main__":   
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = "0.0.0.0"
    port = 3000
    
    try:
        s.bind((host, port))
    except socket.error as e:
        print(str(e))
    s.listen(5)
    
    print(f'[+] Server started ({host}:{port}). Waiting for connections...')

    while True:
        (clientSocket, clientAddress) = s.accept()
        on_new_client(clientSocket, clientAddress)
    s.close()
