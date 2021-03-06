import pygame
import sys
import time
from random import choice, randrange
from pickle import load, dump


pygame.init()
pygame.font.init()
pygame.mixer.init()
start_time = time.time()

# music
background_music = pygame.mixer.Sound("./music/lord_shen.mp3")
background_music.set_volume(0.3)
background_music.play()

laser_shot = pygame.mixer.Sound("./music/laser_shot.mp3")
laser_charge = pygame.mixer.Sound("./music/laser_charge.mp3")
meteor_hit = pygame.mixer.Sound("./music/meteor_hit.mp3")
meteor_hit.set_volume(0.5)

fps = 60
clock = pygame.time.Clock()

# Screen
s_width, s_height = 1536, 864
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption("Meteor Destroy")

# Variables
background = (42, 45, 51)
score = 0
laser_interval = 1000
laser_fire = False
laser_timer = 0
meteor_time = 250
powerup_volume = [0, 0, 0]

# User events
meteor_event = pygame.USEREVENT
time_event = pygame.USEREVENT + 1
meteor_deactivation_event = pygame.USEREVENT + 2
laser_deactivation_event = pygame.USEREVENT + 3
spaceship_deactivation_event = pygame.USEREVENT + 4


# Groups
meteor_grp = pygame.sprite.Group()
laser_grp = pygame.sprite.Group()
powerup_grp = pygame.sprite.Group()


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, img_path, img_path2, img_path3, img_path4, x_pos, y_pos):
        super().__init__()
        self.charged = pygame.image.load(img_path2)
        self.uncharged = pygame.image.load(img_path)
        self.image = self.uncharged
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.health = 5
        self.meteors_destroyed = 0
        self.spaceship_bubble_uncharged = pygame.image.load(img_path3)
        self.spaceship_bubble_charged = pygame.image.load(img_path4)
        self.activated = False

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
        health_img = pygame.image.load("./images/shield.png")
        for index, shield in enumerate(range(self.health)):
            screen.blit(health_img, (index * 40 + 10, 10))

    def charger(self):
        if self.activated == False:
            self.image = self.charged
        else:
            self.image = self.spaceship_bubble_charged

    def uncharger(self):
        if self.activated == False:
            self.image = self.uncharged
        else:
            self.image = self.spaceship_bubble_uncharged

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
        self.image = pygame.image.load("./images/Laser.png")
        self.rect = self.image.get_rect(center=(pos))
        self.speed = 30

    def update(self):
        self.rect.centery -= self.speed
        if self.rect.centery < -20:
            self.kill()


spaceship = SpaceShip(
    "./images/spaceship.png",
    "./images/spaceship_charged.png",
    "./images/spaceship_bubbled.png",
    "./images/spaceship_bubbled_charged.png",
    100,
    100,
)
spaceship_grp = pygame.sprite.GroupSingle()
spaceship_grp.add(spaceship)


def show_powerups(pwr_up1, pwr_up2, pwr_up3):
    screen.blit(pwr_up1, (10 - 5 + 10, 50))
    screen.blit(pwr_up2, (60 - 5 + 10, 50))
    screen.blit(pwr_up3, (110 - 5 + 10, 50))


meteor_act = False


def activate_meteor_powerup():
    global meteor_act, meteor_time
    global powerup3, powerup3_activated, powerup3_deactivated
    if meteor_act == False:
        powerup3 = powerup3_activated
        meteor_act = True
        pygame.time.set_timer(meteor_deactivation_event, 7000)
        for meteors in meteor_grp:
            meteors.y_speed -= 5


def deactivate_meteor_powerup():
    global meteor_act, powerup3, powerup3_deactivated, meteor_time
    if meteor_act == True:
        powerup3 = powerup3_deactivated
        meteor_act = False
        meteor_time = 250


laser_act = False


def activate_laser_powerup():
    global laser_act, laser_interval
    global powerup1, powerup1_activated
    if laser_act == False:
        powerup1 = powerup1_activated
        laser_interval = 500
        pygame.time.set_timer(laser_deactivation_event, 5000)
        laser_act = True


def deactivate_laser_powerup():
    global laser_act, powerup1, powerup1_deactivated, laser_interval
    if laser_act == True:
        powerup1 = powerup1_deactivated
        laser_act = False
        laser_interval = 500 * 2


spaceship_act = False


def activate_spaceship_powerup():
    global powerup2, powerup2_activated, spaceship_act, powerup2_deactivated
    if spaceship_act == False:
        powerup2 = powerup2_activated
        spaceship_act = True
        pygame.time.set_timer(spaceship_deactivation_event, 5000)
        spaceship_grp.sprite.activated = True


def deactivate_spaceship_powerup():
    global spaceship_act, powerup2, powerup2_deactivated
    if spaceship_act == True:
        powerup2 = powerup2_deactivated
        spaceship_act = False
        spaceship_grp.sprite.activated = False


# Keys


def powerup_keys():
    font = pygame.font.Font("./fonts/nasalization.otf", 15)
    font_render1 = font.render("L", 1, pygame.Color("white"))
    font_render2 = font.render("S", 1, pygame.Color("white"))
    font_render3 = font.render("M", 1, pygame.Color("white"))
    font1_rect = font_render1.get_rect(center=(15 + 18, 100))
    font2_rect = font_render2.get_rect(center=(65 + 18, 100))
    font3_rect = font_render3.get_rect(center=(115 + 18, 100))
    screen.blit(font_render1, font1_rect)
    screen.blit(font_render2, font2_rect)
    screen.blit(font_render3, font3_rect)


# Powerups Images
powerup1_deactivated = pygame.image.load("./images/powerup1.png")
powerup2_deactivated = pygame.image.load("./images/powerup2.png")
powerup3_deactivated = pygame.image.load("./images/powerup3.png")
powerup1_activated = pygame.image.load("./images/powerup1_activated.png")
powerup2_activated = pygame.image.load("./images/powerup2_activated.png")
powerup3_activated = pygame.image.load("./images/powerup3_activated.png")
powerup1 = powerup1_deactivated
powerup2 = powerup2_deactivated
powerup3 = powerup3_deactivated

pygame.time.set_timer(meteor_event, meteor_time)
pygame.time.set_timer(time_event, 1000)


def high_score():
    with open("high_score.dat", "rb") as f:
        contents = load(f)[0]
        return contents


def write_high_score(score):
    with open("high_score.dat", "rb") as f:
        scores = load(f)
    with open("high_score.dat", "wb") as f2:
        scores[0] = score
        dump(scores, f2)


def show_fps():
    font = pygame.font.Font("./fonts/Pixellari.ttf", 20)
    font_render = font.render(
        f"{int(clock.get_fps())}", 1, pygame.Color("white"))
    screen.blit(font_render, (0, s_height - font_render.get_height()))


def meteor_gen():
    meteor_img = choice(
        ("./images/meteor1.png", "./images/meteor2.png", "./images/meteor3.png"))
    x_pos = randrange(50, 1230)
    y_pos = randrange(-150, -50)
    x_speed = randrange(0, 2)
    y_speed = randrange(8, 12)
    meteor = Meteor(meteor_img, x_pos, y_pos, x_speed, y_speed)
    meteor_grp.add(meteor)


def main_logic():
    global laser_fire, laser_interval
    if pygame.sprite.groupcollide(laser_grp, meteor_grp, True, True):
        spaceship_grp.sprite.meteors_destroyed += 1
    if spaceship_grp.sprite.activated == True and pygame.sprite.spritecollide(
        spaceship_grp.sprite, meteor_grp, True
    ):
        meteor_hit.play()
    elif spaceship_grp.sprite.activated == False and pygame.sprite.spritecollide(
        spaceship_grp.sprite, meteor_grp, dokill=True
    ):
        spaceship_grp.sprite.damage()
        meteor_hit.play()

    laser_grp.draw(screen)
    spaceship_grp.draw(screen)
    laser_grp.update()
    spaceship_grp.update()
    meteor_grp.draw(screen)
    meteor_grp.update()
    powerup_keys()

    show_powerups(powerup1, powerup2, powerup3)
    if pygame.time.get_ticks() - laser_timer >= laser_interval:
        laser_fire = True
        spaceship_grp.sprite.charger()
    return 1


def end_game():
    high_scoore = high_score()
    if spaceship_grp.sprite.health <= 0:
        if score > high_scoore:
            write_high_score(score)
        font = pygame.font.Font("./fonts/nasalization.otf", 50)
        font_render = font.render("Game Over", 1, pygame.Color("white"))
        font_rect = font_render.get_rect(
            center=(s_width / 2, s_height / 2 - 50))
        screen.blit(font_render, font_rect)
        font2 = pygame.font.Font("./fonts/nasalization.otf", 40)
        font_render2 = font2.render(
            f"Score: {score}", 1, pygame.Color("white"))
        font_rect2 = font_render2.get_rect(
            center=(s_width / 2, s_height / 2 + font_render.get_height() - 50)
        )
        screen.blit(font_render2, font_rect2)
        font_render4 = font2.render(
            f"High Score: {high_scoore}", 1, pygame.Color("white")
        )
        font_rect4 = font_render4.get_rect(
            center=(
                s_width / 2,
                s_height / 2
                + font_render.get_height()
                + font_render4.get_height()
                - 50,
            )
        )
        font3 = pygame.font.Font("./fonts/nasalization.otf", 20)
        font_render3 = font3.render(
            f"Meteors Destroyed: {spaceship_grp.sprite.meteors_destroyed}",
            1,
            pygame.Color("white"),
        )
        font_rect3 = font_render3.get_rect(
            center=(
                s_width / 2,
                s_height / 2
                + font_render2.get_height()
                + font_render.get_height()
                + font_render4.get_height()
                - 50,
            )
        )
        screen.blit(font_render3, font_rect3)
        screen.blit(font_render4, font_rect4)


run = True
while run:
    screen.fill(background)
    clock.tick(fps)
    if spaceship_grp.sprite.health > 0:
        score += main_logic()
    else:
        end_game()
    # display frame rate
    show_fps()

    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            run = False
            sys.exit()
        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_q:
                run = False
                sys.exit()
            if events.key == pygame.K_s:
                activate_spaceship_powerup()
            if events.key == pygame.K_l:
                activate_laser_powerup()
            if events.key == pygame.K_m:
                activate_meteor_powerup()
        if events.type == meteor_event:
            meteor_gen()
        if events.type == laser_deactivation_event:
            deactivate_laser_powerup()
        if events.type == meteor_deactivation_event:
            deactivate_meteor_powerup()

        if events.type == spaceship_deactivation_event:
            deactivate_spaceship_powerup()
        if events.type == pygame.MOUSEBUTTONDOWN and laser_fire:
            laser = Laser("./images/Laser.png", events.pos)
            laser_grp.add(laser)
            laser_timer = pygame.time.get_ticks()
            laser_fire = False
            laser_shot.play()
            spaceship_grp.sprite.uncharger()
            laser_charge.play()
        if events.type == pygame.MOUSEBUTTONDOWN and spaceship_grp.sprite.health <= 0:
            spaceship_grp.sprite.health = 5
            meteor_grp.empty()
            score = 0
            spaceship_grp.sprite.meteors_destroyed = 0
            meteor_time = 250
            spaceship_act = False
            meteor_act = False
            laser_act = False
    pygame.display.update()
