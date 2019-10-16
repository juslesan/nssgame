import pygame

class Wall():
    def __init__(self, startX, startY, width, height):
        self.x = startX
        self.y = startY
        self.width = width
        self.height = height
    def draw(self, g): 
        pygame.draw.rect(g, (100,100,100), (self.x, self.y, self.width, self.height))
        
