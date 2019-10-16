import pygame
import math

class Player():


    def __init__(self, startx, starty, id, hp, upgrades, walls, color=(255,0,0)):
        self.x = startx
        self.y = starty
        self.rad = 15
        self.velocity = 5
        self.color = color
        self.healthpoints = hp
        self.upgrades = upgrades

        self.angle = 0
        self.id = id
        self.walls = walls
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
       