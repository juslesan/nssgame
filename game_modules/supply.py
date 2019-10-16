import pygame

class Supply():
    def __init__(self, x, y, category):
        self.x = x
        self.y = y
        self.category = category
    
    def draw(self, g):
        if self.category == "hp":
            pygame.draw.rect(g, (200,0,0), (self.x, self.y, 10, 10))
        else:
            pygame.draw.rect(g, (0,0,0), (self.x, self.y, 10, 10))
