import pygame
import sys
from random import choice, randrange

# TODO: add an highscore
# TODO: add 3 powerups
# TODO: difficulty increase

pygame.init()
pygame.font.init()
pygame.mixer.init()

fps = 60
clock = pygame.time.Clock()

# Screen
s_width, s_height = 1280, 720
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption("Meteor Destroy")
background = (42, 45, 51)


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, img_path, img_path2, x_pos, y_pos) -> None:
        super().__init__()
        self.charged = pygame.transform.scale(pygame.image.load(img_path2), (100, 60))
        self.uncharged = pygame.transform.scale(pygame.image.load(img_path), (100, 60))
        self.image = self.uncharged
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.health = 5

    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        self.constraints()
        self.display_health()

    def constraints(self):
        if self.rect.right > s_width:
            self.rect.right = s_width
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > s_height:
            self.rect.bottom = s_height
        if self.rect.top < 0:
            self.rect.top = 0

    def display_health(self):
        health_img = pygame.image.load("shield.png")
        for index, shield in enumerate(range(self.health)):
            # screen.blit(health_img, (index+20, 10))#! why it does not work?
            # ? Ans: if we consider the indexes we'll end up with 0,1,2,3,4 and if we add 20 to all of them we'll get 20,21,22,23,24 which is really difficult to see as their is only 1 pixel distance
            # print((index+20, 10))
            # print((index*40, 10))
            screen.blit(health_img, (index * 40 + 10, 10))

    def charger(self):
        self.image = self.charged

    def uncharger(self):
        self.image = self.uncharged

    def damage(self):
        self.health -= 1
        if self.health <= 0:
            self.health = 0


class Meteor(pygame.sprite.Sprite):
    def __init__(self, img_path, x_pos, y_pos, x_speed, y_speed) -> None:
        super().__init__()
        self.image = pygame.image.load(img_path)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.x_speed = x_speed
        self.y_speed = y_speed

    def update(self):
        self.rect.right += self.x_speed
        self.rect.bottom += self.y_speed
        if self.rect.bottom >= s_height + 100:
            self.kill()


class Laser(pygame.sprite.Sprite):
    def __init__(self, img_path, pos):
        super().__init__()
        self.image = pygame.image.load("./Laser.png")
        self.rect = self.image.get_rect(center=(pos))
        self.speed = 30

    def update(self):
        self.rect.centery -= self.speed
        if self.rect.centery < -100:
            self.kill()


laser_grp = pygame.sprite.Group()

spaceship = SpaceShip("spaceship.png", "spaceship_charged.png", 100, 100)
spaceship_grp = pygame.sprite.GroupSingle()
spaceship_grp.add(spaceship)


meteor_grp = pygame.sprite.Group()
METEOR_EVENT = pygame.USEREVENT
# ? pygame.time.set_timer(<Event to trigger>,<time in milliseconds>)
pygame.time.set_timer(METEOR_EVENT, 250)
# meteor_grp.add(meteor)


def show_fps():
    font = pygame.font.Font("./Pixellari.ttf", 20)
    font_render = font.render(f"{int(clock.get_fps())}", 1, pygame.Color("white"))
    screen.blit(font_render, (0, s_height - font_render.get_height()))


def meteor_gen():
    meteor_img = choice(("meteor1.png", "meteor2.png", "meteor3.png"))
    x_pos = randrange(50, 1230)
    y_pos = randrange(-150, -50)
    x_speed = randrange(0, 2)
    y_speed = randrange(5, 12)
    meteor = Meteor(meteor_img, x_pos, y_pos, x_speed, y_speed)
    meteor_grp.add(meteor)


def main_logic():
    if pygame.sprite.spritecollide(spaceship_grp.sprite, meteor_grp, dokill=True):
        spaceship_grp.sprite.damage()
    for laser in laser_grp:
        pygame.sprite.spritecollide(laser, meteor_grp, dokill=True)
    laser_grp.draw(screen)
    spaceship_grp.draw(screen)
    laser_grp.update()
    spaceship_grp.update()
    meteor_grp.draw(screen)
    meteor_grp.update()


def end_game():
    if spaceship_grp.sprite.health <= 0:
        font = pygame.font.Font("Pixellari.ttf", 50)
        font_render = font.render("Game Over", 1, pygame.Color("white"))
        font_rect = font_render.get_rect(center=(s_width / 2, s_height / 2))
        screen.blit(font_render, font_rect)
        # pygame.time.delay(1000)


run = True
while run:
    screen.fill(background)
    clock.tick(fps)
    if spaceship_grp.sprite.health > 0:
        main_logic()
    else:
        end_game()
    show_fps()

    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            run = False
            sys.exit()
        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_q:
                run = False
                sys.exit()
        if events.type == METEOR_EVENT:
            meteor_gen()
        if events.type == pygame.MOUSEBUTTONDOWN:
            laser = Laser("Laser.png", events.pos)
            laser_grp.add(laser)
        if events.type == pygame.MOUSEBUTTONDOWN and spaceship_grp.sprite.health <= 0:
            spaceship_grp.sprite.health = 5
            meteor_grp.empty()

    pygame.display.update()
