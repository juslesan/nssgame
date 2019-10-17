import socket
from _thread import *
import sys
import pygame
import math
import random

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = 'localhost'
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

currentId = 0
pos = []
hps = {}
upgrades = {}
shots = []
supply = []
options = ""

def remove_lost(thread_id):
    global pos, hps
    for i in range(len(pos)):
        #print(int(pos[i].split(":")[0]))
       # print(thread_id)
        if thread_id == int(pos[i].split(":")[0]):
            pos.remove(pos[i])
            del hps[thread_id]
            del upgrades[thread_id]
            #print("here")

def threaded_client(conn):
    global currentId, pos, hps, upgrades, options
    #print(options)
    conn.send(str.encode(str(currentId) + ";" + str(options).strip("[").strip("]").strip("'")))
    thread_id = currentId
    currentId += 1
    reply = ''
    while True:
        try:
            data = conn.recv(4096)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break  
            else:
                print("Received: " + reply)
                arr = reply.split(":")
                id = int(arr[0])
                split = arr[1].split(",")

                # check if packet is new shot
                if split[0] == "NS":
                    shot = split[1:]
                    shots.append(shot)

                #check if packet is new player
                else:
                    included = False
                    for i in range(len(pos)):
                        if pos[i].split(":")[0] == arr[0]:
                            included = True
                            pos[i] = str(arr[0]) + ":" + str(arr[1])
                    if included == False:
                        pos.append(reply)
                        hps[thread_id] = 3
                        upgrades[thread_id] = 0
                    
                # Check if player is still alive
                alive = True
                for i in range(len(pos)):
                    sp = pos[i].split(":")
                    if hps[int(sp[0])] == 0 and int(sp[0]) == thread_id:
                        alive = False                        
                        break  
                if alive == False:
                    conn.send(str.encode("You have died"))
                    break
                
                #Start building a reply message for the client
                reply = ""
                #Add position and health of players
                for i in range(len(pos)):
                    reply += pos[i]
                    reply += "," + str(hps[int(pos[i].split(":")[0])])
                    reply += "," + str(upgrades[int(pos[i].split(":")[0])])
                    reply += ";"
                reply = reply[:(len(reply) - 1)]
                reply += "_"

                #Add positions of shots in the server
                for shot in shots:
                    stri = ""
                    for i in range(len(shot)):
                        stri += shot[i] 
                        if (i < len(shot)-1):
                            stri += ','
                    reply += stri
                    reply += ";"
                if (len(shots) > 0):
                    reply = reply[:-1]
                reply += "_"

                #Add positions of supply drops in the server
                for sup in supply:
                    reply += sup
                    reply += ";"
                if (len(supply) > 0):
                    reply = reply[:-1]
                #print(pos)
                print("Sending: " + reply)

            conn.sendall(str.encode(reply))

        except Exception as e: 
            print(e)
            remove_lost()
            break

    #If the threaded connection to the client is broken
    print("Connection Closed")
    conn.close()
    remove_lost(thread_id)

def check_if_player_over_rect(rect_pos, rect_size, circle_pos):
    rect = pygame.Rect(rect_pos , rect_size)
    centerPt = pygame.math.Vector2(circle_pos)
    cornerPts = [rect.bottomleft, rect.bottomright, rect.topleft, rect.topright]
    if [p for p in cornerPts if pygame.math.Vector2(*p).distance_to(centerPt) <= 15]:
        return True
    return False

def scan_supply():
    global pos, hps, supply
    supply_to_remove = []
    # Check for each supply drop if a player collides with it, max 2 supply drops in the field at once no significant performance decreases here.
    for i in range(len(supply)):
        for po in range(len(pos)):
            split = pos[po].split(":")
            possplit = split[1].split(",")
            supplysplit = supply[i].split(":")
            supplypos = supplysplit[1].split(",")

            # Check if player lands on supply drop
            if (check_if_player_over_rect((int(supplypos[0]), int(supplypos[1])) , (10,10), (float(possplit[0]), float(possplit[1])))):
                    # Make the player that was hit lose health
                    supply_to_remove.append(supply[i])
                    if supplysplit[0] == "hp":
                        hps[int(split[0])] += 1
                    if supplysplit[0] == "sh":
                        upgrades[int(split[0])] += 1
                    break
    for sup in supply_to_remove:
        supply.remove(sup)

def scan_hits():
    global pos, shots, hps, upgrades
    shots_to_remove = []
    # Need to for loop the shots and players to scan hits per server tick, a performance bottleneck    
    for i in range(len(shots)):
        for po in range(len(pos)):
            split = pos[po].split(":")
            possplit = split[1].split(",")
            if (shots[i][5] != split[0]):
                #Check if the shot hits a players
                if check_if_player_over_rect((float(shots[i][0]), float(shots[i][1])),(int(shots[i][2]),int(shots[i][2])), (float(possplit[0]), float(possplit[1]))):
                    # Make the player that was hit lose health
                    shots_to_remove.append(shots[i])
                    hps[int(split[0])] -= 1
                    if (hps[int(split[0])] < 0):
                        hps[int(split[0])] = 0
                    break
    # print(shots_to_remove)
    for shot in shots_to_remove:
        shots.remove(shot)

def parse_options():
    global options
    x = 0
    y = 0
    walls = []
    split_options = options.split(",")
    for i in range(len(split_options)):
        if i == 0:
            x = int(split_options[i])
        elif i == 1:
            y = int(split_options[i])
        else:
            walls.append(split_options[i])
    #print(walls)
    return [x, y, walls]

def gametime():
    global shots, supply, pos
    clock = pygame.time.Clock()
    opts = parse_options()
    #print(opts)
    while (True):
        clock.tick(60)
        # Add supply drops with 0.05% chance per server tick, max 2 supply drop on map at all times
        if random.randint(1, 10000) > 9950 and pos != [] and len(supply) < 1:
            supply.append("hp:" + str(random.randint(10, 590)) + "," + str(random.randint(10, 590)))
            supply.append("sh:" + str(random.randint(10, 590)) + "," + str(random.randint(10, 590)))
        # Update all the shots by adding their vector values to their current positions.
        filtered_shots = [] 
        for i in range(len(shots)):
            shots[i][0] = str(float(shots[i][3]) + float(shots[i][0]))
            shots[i][1] = str(float(shots[i][4]) + float(shots[i][1]))

            # Remove shot if out of bounds
            if float(shots[i][0]) < int(opts[0]) and float(shots[i][0]) > 0 and float(shots[i][1]) < int(opts[1]) and float(shots[i][1]) > 0:
                for wall in opts[2]:
                    #print(here)
                    spl = wall.split(":")
                    rect = pygame.Rect((int(spl[0]), int(spl[1])),(int(spl[2]),int(spl[3])))
                    hit = False
                    if rect.collidepoint(float(shots[i][0]), float(shots[i][1])):
                        hit = True
                        break
                if hit == False:
                    filtered_shots.append(shots[i]) 
        shots = filtered_shots

        scan_hits()
        scan_supply()

mappath = str(sys.argv[1])
try:
    f = open("map", "r")
    line = f.readline()
    cnt = 0
    while line:
        opt = str(line).rsplit()[0] + ","
        #print(opt)
        options += opt
        line = f.readline()
        cnt += 1
finally:
    options = options[:-1]
    f.close()
#print(options)

# Start thread that keeps up the game servers tick rate.
start_new_thread(gametime,())
while True:
    # Accept new connections from clients
    conn, addr = s.accept()
    print("Connected to: ", addr)
    # Start a new client thread for new connection
    start_new_thread(threaded_client, (conn,))

    