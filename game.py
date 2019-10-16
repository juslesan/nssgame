import pygame
from network import Network
import math
from _thread import *
import random
from game_modules.player import Player
from game_modules.shot import Shot
from game_modules.supply import Supply
from game_modules.wall import Wall
from game_modules.canvas import Canvas

class Game:

    def __init__(self, w, h):
        self.net = Network()
        self.width = int(self.net.options[0])
        self.cooldown = False
        self.height = int(self.net.options[1])
        self.players = []
        self.supply = []
        self.canvas = Canvas(self.width, self.height, "Testing")
        self.walls = []
        for wall in self.net.options[2:]:
            splt = wall.split(":")
            print(splt)
            self.walls.append(Wall(int(splt[0]), int(splt[1]), int(splt[2]), int(splt[3])))

        self.player = Player(random.randint(10, w), random.randint(10, h), self.net.id, 3, 0, self.walls)

    def run_cooldown(self, wait):
        global cooldown
        pygame.time.wait(wait)
        self.cooldown = False

    def run(self):
        clock = pygame.time.Clock()
        running = True
        angle = 0
        shots = []
        pygame.font.init()
        myfont = pygame.font.SysFont('Arial', 20)

        while running:
            clock.tick(30)
            mouse_position = pygame.mouse.get_pos()

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
                    vel_x = math.cos(angle) * 5
                    vel_y = math.sin(angle) * 5

                    self.net.send(str(self.net.id) + ":" + "NS," + str(self.player.x) + "," + str(self.player.y) + "," + str(self.player.upgrades + 5) + "," + str(vel_x) + "," + str(vel_y)+ "," + self.net.id)
                    self.cooldown = True
                    start_new_thread(self.run_cooldown,(400,))
            
            # Send Network Stuff
            network_unsplit = self.send_data()
            print(network_unsplit)
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

            # Parse player positions from message
            players_new = []
            for pos in parsed_positions:
                splitId = pos.split(":")
                id = splitId[0]
                # print(id)
                split = splitId[1].split(",")
                if id != self.net.id:
                    players_new.append(Player(int(split[0]), int(split[1]), id, int(split[2]), int(split[3]), []))
                else:
                    self.player.update_hp_upgrades(int(split[2]), int(split[3]))
            self.players = players_new        

            # Parse shot positions from message
            new_shots = []
            for shot in parsed_shots:
                if shot != '':
                    listed = shot.split(",")
                   # print(listed)
                    if (len(listed) > 3):  
                        new_shots.append(Shot(float(listed[0]), float(listed[1]), int(listed[2]), (255,0,0)))    
            #print(new_shots)
            self.shots = new_shots     

            # Parse supply drops from message
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

            # Render the game
            self.canvas.draw_background()
            for wall in self.walls:
                wall.draw(self.canvas.get_canvas())
            self.player.draw(self.canvas.get_canvas())
            #self.player2.draw(self.canvas.get_canvas())
            for pl in self.players:
                pl.draw(self.canvas.get_canvas())
            for shot in self.shots:
                shot.draw(self.canvas.get_canvas())
            for supply in self.supply:
                supply.draw(self.canvas.get_canvas())
            self.canvas.draw_text("hp: " + str(self.player.healthpoints) + " ups: " + str(self.player.upgrades), 18, 10, 10)
            self.canvas.update()
           
        pygame.quit()

    def send_data(self):
        """ 
        Send position to server
        :return: None   
        """
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
