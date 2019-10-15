import pygame
from network import Network
import math
from _thread import *
import random

class Player():


    def __init__(self, startx, starty, id, hp, upgrades, color=(255,0,0)):
        self.x = startx
        self.y = starty
        self.rad = 15
        self.velocity = 3
        self.color = color
        self.healthpoints = hp
        self.upgrades = upgrades

        self.angle = 0
        self.id = id
    def draw(self, g):
        pygame.draw.circle(g, self.color ,(self.x, self.y), self.rad)

    def update(self, x, y):
        self.x = x
        self.y = y
    def update_hp_upgrades(self, hp, upgrades):
        self.healthpoints = hp
        self.upgrades = upgrades

    def move(self, dirn):
        """
        :param dirn: 0 - 3 (right, left, up, down)
        :return: None
        """

        if dirn == 0:
            self.x += self.velocity
        elif dirn == 1:
            self.x -= self.velocity
        elif dirn == 2:
            self.y -= self.velocity
        else:
            self.y += self.velocity
       
class Shot():

    def __init__(self, startx, starty, width, color):
        self.x = startx
        self.y = starty
        self.width = width
       # self.velocityX = velocityX
       # self.velocityY = velocityY
        self.color = color

    def draw(self, g):
        pygame.draw.rect(g, self.color, (self.x, self.y, self.width, self.width))

    def update(self, x, y):
        self.x += self.x
        self.y += self.y

    def out_of_bounds(self, canvasX, canvasY):
        if self.x < 0 or self.x > canvasX or self.y < 0 or self.y > canvasY:
            return True
        return False

class Supply():
    def __init__(self, x, y, category):
        self.x = x
        self.y = y
        self.category = category
    
    def draw(self, g):
        print(self.category)
        if self.category == "hp":
            pygame.draw.rect(g, (200,0,0), (self.x, self.y, 10, 10))
        else:
            pygame.draw.rect(g, (0,0,0), (self.x, self.y, 10, 10))
class Game:

    def __init__(self, w, h):
        self.net = Network()
        self.width = w
        self.cooldown = False
        self.height = h
        self.player = Player(random.randint(10, w), random.randint(10, h), self.net.id, 3, 0)
        self.players = []
        self.supply = []
        self.canvas = Canvas(self.width, self.height, "Testing...")

    def list_player_ids(self):
        ids = []
        if len(self.players) == 0:
            return []
        for player in self.players:
            ids.append(player.id)
        return ids
        
    def find_player_by_id(self, id):
        for player in self.players:
            if player.id == id:
                return player
            else:
                return {}


    def run_cooldown(self, wait):
        global cooldown
        pygame.time.wait(wait)
        self.cooldown = False

    def run(self):
        clock = pygame.time.Clock()
        running = True
        angle = 0
        shots = []
        while running:
            clock.tick(60)
 
            mouse_position = pygame.mouse.get_pos()
            # Distances to the mouse position.

            rise = mouse_position[1] - self.player.y
            run = mouse_position[0] - self.player.x
            angle = math.atan2(rise, run)
           # print(rise, " ", run, " ", angle)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.K_ESCAPE:
                    running = False
    
            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if self.player.x <= self.width - self.player.velocity:
                    self.player.move(0)

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if self.player.x >= self.player.velocity:
                    self.player.move(1)

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                if self.player.y >= self.player.velocity:
                    self.player.move(2)

            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if self.player.y <= self.height - self.player.velocity:
                    self.player.move(3)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.cooldown == False:
                    vel_x = math.cos(angle) * 4
                    vel_y = math.sin(angle) * 4

                    self.net.send(str(self.net.id) + ":" + "NS," + str(self.player.x) + "," + str(self.player.y) + "," + str(self.player.upgrades + 5) + "," + str(vel_x) + "," + str(vel_y)+ "," + self.net.id)
                    self.cooldown = True
                    start_new_thread(self.run_cooldown,(400,))
            
            # Send Network Stuff
            network_unsplit = self.send_data()
            if (network_unsplit == "You have died"):
                print(network_unsplit)
                break
            #print(network_unsplit)
            network_data = self.split_data(network_unsplit)
            # print(network_data)
            if len(network_data) == 3:
                parsed_positions = self.parse_data(network_data[0])
                parsed_shots = self.parse_data(network_data[1])
                parsed_supply = self.parse_data(network_data[2])

            else:
                parsed_positions = []
                parsed_shots = []
                parsed_supply = []

            # print()
            players_new = []
            for pos in parsed_positions:
                splitId = pos.split(":")
                id = splitId[0]
                # print(id)
                split = splitId[1].split(",")
                if id != self.net.id:
                    players_new.append(Player(int(split[0]), int(split[1]), id, int(split[2]), int(split[3])))
                else:
                    self.player.update_hp_upgrades(int(split[2]), int(split[3]))
            self.players = players_new        

            new_shots = []
            for shot in parsed_shots:
                if shot != '':
                    listed = shot.split(",")
                   # print(listed)
                    if (len(listed) > 3):  
                        new_shots.append(Shot(float(listed[0]), float(listed[1]), int(listed[2]), (255,0,0)))    
            #print(new_shots)
            self.shots = new_shots     

            supply_new = []
            for supply in parsed_supply:
                #print(supply)
                splitsupply = supply.split(":")
                category = splitsupply[0]
                # print(id)
                if (len(splitsupply) > 1):
                    split = splitsupply[1].split(",")
                    supply_new.append(Supply(int(split[0]), int(split[1]), category))

            self.supply = supply_new

            self.canvas.draw_background()
            self.player.draw(self.canvas.get_canvas())
            #self.player2.draw(self.canvas.get_canvas())
            for pl in self.players:
                pl.draw(self.canvas.get_canvas())
            for shot in self.shots:
                shot.draw(self.canvas.get_canvas())
            for supply in self.supply:
                supply.draw(self.canvas.get_canvas())
            self.canvas.update()
           
        pygame.quit()

    def send_data(self):
        """
        Send position to server
        :return: None
        """
        print(self.player.healthpoints)
        print(self.player.upgrades)
        data = str(self.net.id) + ":" + str(self.player.x) + "," + str(self.player.y)
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(";")
            #print(d)
            return d
        except:
            return []

    def split_data(self, data):
        try:
            d = data.split("_")
            # print(d)
            return d
        except:
            return []

class Canvas:

    def __init__(self, w, h, name="None"):
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w,h))
        pygame.display.set_caption(name)

    @staticmethod
    def update():
        pygame.display.update()

    def draw_text(self, text, size, x, y):
        pygame.font.init()
        font = pygame.font.SysFont("comicsans", size)
        render = font.render(text, 1, (0,0,0))

        self.screen.draw(render, (x,y))

    def get_canvas(self):
        return self.screen

    def draw_background(self):
        self.screen.fill((255,255,255))