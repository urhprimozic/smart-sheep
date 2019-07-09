# this is not used to make Object-oriented game engine from pygame
# it just makes the coding later on shorter
import pygame
import os
import settings
import pygame.freetype

dir_name = os.path.dirname(__file__)
pygame.init()
pygame.freetype.init()
font = pygame.freetype.Font(os.path.join(dir_name, 'font/Roboto-Light.ttf'), 22)


class Text:
    def __init__(self, string):
        self.string = string

    def render(self, color, x, y, size, screen):
        font.render_to(screen, (x, y), self.string, color)
        # pygame.display.flip()


class Object:
    # watch for y!!!*
    def __init__(self, sprites, x=0, y=0):
        self.surfaces = [pygame.image.load(os.path.join(dir_name, i)).convert_alpha() for i in sprites]
        # I would do this with pointers in C++. How to efficiently do this in Pythnon? @ me
        self.surface_counter = 0
        self.mask = self.surfaces[self.surface_counter].get_rect()
        self.mask.x = x
        self.mask.y = y - self.mask.height  # *
        self.alive = True
        self.hunger = 0.0
        self.vy = 0

    def animate(self):
        self.surface_counter += 1
        if self.surface_counter == len(self.surfaces):
            self.surface_counter = 0

    def move_to(self, x, y):
        self.mask.x = x
        self.mask.y = y

    def move_to_x(self, x):
        self.mask.x = x

    def move_by(self, dx, dy):
        self.mask.x += dx
        self.mask.y += dy

    def kill(self):
        self.alive = False
        self.move_to(-settings.width, -settings.height)

    def render(self, screen):
        screen.blit(self.surfaces[self.surface_counter], self.mask)
        # pygame.display.flip()

    def in_bounds(self, w=settings.width, h=settings.height):
        if self.mask.x >= 0 and self.mask.y >= 0 and self.mask.right <= w and self.mask.bottom <= h:
            return True
        else:
            return False

    def x_bounds(self, w=settings.width):
        if self.mask.right >= 0 and self.mask.x <= w:
            return 1
        return 0

    def collision(self, other):
        if self.mask.colliderect(other.mask):
            return True
        return False


def in_bounds(x, y, a, b, w, h):
    if a < x < a + w and b < y < b + h:
        return True
    return False
