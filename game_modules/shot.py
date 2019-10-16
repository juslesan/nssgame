import pygame
import math

class Shot():

    def __init__(self, startx, starty, width, color):
        self.x = startx
        self.y = starty
        self.width = width
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