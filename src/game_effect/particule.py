import pygame
import random
from pygame.locals import *
from src.tools.tools import Vector2, sprite_sheet
import src.tools.constant as tl
from src.tools.constant import PATH

SP = sprite_sheet(PATH / "assets" / "UI" / "numbers.png", (10, 11))
SP.dico = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, "%": 10}


class Particule(pygame.sprite.Sprite):
    """ MAIN CLASS OF THE SCRIPT"""

    def __init__(self, lifetime, position: Vector2, range, direction: Vector2, speed, teinte: pygame.Color, gravity=False, size=(3, 3)):
        super().__init__()
        self.lifetime = lifetime * random.uniform(0.9, 1.1)
        self.position = Vector2(position.x + random.randrange(-range, range), position.y)
        self.direction = Vector2(direction.x + random.randrange(-1, 1), direction.y + random.randrange(-1, 1))
        self.gravity = gravity
        self.speed = speed

        self.image = pygame.transform.scale(pygame.image.load(PATH / "assets" / "particle.png"), size)
        self.image = pygame.transform.rotate(self.image, random.randrange(0, 90))
        li_loss = random.randrange(0, 55)
        li_teinte = pygame.Color(teinte.r - min(teinte.r, teinte.g, teinte.b), teinte.g - min(teinte.r, teinte.g, teinte.b), teinte.b - min(teinte.r, teinte.g, teinte.b))
        self.image.fill((min(255 - li_loss + li_teinte.r, 255), min(255 - li_loss + li_teinte.g, 255), min(255 - li_loss + li_teinte.b, 255)))
        self.rect = self.image.get_rect(topleft=self.position())

    def move(self, serialized):
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")

        _dx = self.direction.x * self.speed * serialized
        _dy = self.direction.y * self.speed * serialized
        self.rect.move_ip(_dx, _dy)

    def handle(self, event: pygame.event.Event):
        """methode appele a chaque event"""
        match event.type:
            case tl.GRAVITY:
                if self.gravity:
                    self.direction.y -= 9.81 / self.speed

    def update(self, serialized, *args, **kargs):
        if self.lifetime < 0:
            self.kill()
        else:
            self.lifetime -= 1
            self.move(serialized)


class AnimatedParticule(pygame.sprite.Sprite):
    def __init__(self, spritesheet: sprite_sheet, lifetime: int, position: Vector2, range, direction: Vector2, speed, gravity):
        super().__init__()
        self.lifetime = lifetime
        self.position = Vector2(position.x + random.randrange(-range, range), position.y)
        self.direction = Vector2(direction.x + random.randrange(-1, 1), direction.y + random.randrange(-1, 1))
        self.gravity = gravity
        self.speed = speed
        self.frame = 0
        self.dframe = (spritesheet.x_nb * spritesheet.y_nb) / lifetime

        self.spritesheet = spritesheet
        self.rect = self.image.get_rect(topleft=self.position())

    @property
    def image(self) -> pygame.Surface:
        return self.spritesheet[int(self.frame)]

    def move(self, serialized):
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")

        _dx = self.direction.x * self.speed * serialized
        _dy = self.direction.y * self.speed * serialized
        self.rect.move_ip(_dx, _dy)

    def handle(self, event: pygame.event.Event):
        """methode appele a chaque event"""
        match event.type:
            case tl.GRAVITY if self.gravity:
                self.direction.y -= 9.81 / self.speed

    def update(self, serialized, *args, **kargs):
        if self.lifetime <= self.frame:
            self.kill()
        else:
            self.frame += self.dframe
            self.move(serialized)


class textParticle(pygame.sprite.Sprite):
    def __init__(self, lifetime, position: Vector2, direction: Vector2, speed, text, size):
        super().__init__()
        self.lifetime = lifetime
        self.position = position
        self.text = text
        self.image: pygame.Surface = pygame.transform.scale(SP[text], size)
        self.rect = self.image.get_rect(topleft=self.position)
        self.direction = direction
        self.speed = speed
        self.time = lifetime

    def move(self, serialized):
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")

        _dx = self.direction.x * self.speed * serialized
        _dy = self.direction.y * self.speed * serialized
        self.rect.move_ip(_dx, _dy)

    def handle(self, event: pygame.event.Event):
        ...

    def update(self, serialized, *args, **kargs):
        if self.time < 0:
            self.kill()
        else:
            self.time -= 1
            self.image.set_alpha(self.time / self.lifetime * 255)
            self.move(serialized)
