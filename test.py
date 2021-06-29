import pygame
import sys
import time
from random import choice, randrange

# TODO: add an highscore
# TODO: add 3 powerups
# TODO: difficulty increase

pygame.init()
pygame.font.init()
pygame.mixer.init()
start_time = time.time()

# music
background_music = pygame.mixer.Sound("lord_shen.mp3")
background_music.set_volume(0.3)
background_music.play()

laser_shot = pygame.mixer.Sound("laser_shot.mp3")
laser_charge = pygame.mixer.Sound("laser_charge.mp3")
meteor_hit = pygame.mixer.Sound("meteor_hit.mp3")
meteor_hit.set_volume(0.5)

fps = 60
clock = pygame.time.Clock()

# Screen
s_width, s_height = 1280, 720
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption("Meteor Destroy")
background = (42, 45, 51)
score = 0
powerup_grp = pygame.sprite.Group()


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, img_path, img_path2, img_path3, x_pos, y_pos) -> None:
        super().__init__()
        self.charged = pygame.image.load(img_path2)
        self.uncharged = pygame.image.load(img_path)
        self.image = self.uncharged
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.health = 5
        self.meteors_destroyed = 0
        self.spaceship_bubble = pygame.image.load(img_path3)

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

    def bubble_powerup(self):
        self.image = self.spaceship_bubble

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
        if self.rect.centery < -20:
            self.kill()

    # screen.blit(powerup1, (10, 50))
    # screen.blit(powerup2, )
    # screen.blit(powerup3, )


class Powerups:
    def __init__(self, normal_image, pos, activated_img):
        self.deactivated = pygame.image.load(normal_image)
        self.activated = pygame.image.load(activated_img)
        self.image = self.deactivated
        self.rect = self.image.get_rect(center=pos)

    def show_on_screen(self):
        screen.blit(self.image, self.rect)


class Laser_Powerup(Powerups):
    laser_interval = 1000

    def __init__(self, normal_image, activated_img, pos, laser_interval):
        super().__init__(normal_image, activated_img, pos)
        self.laser_interval = laser_interval

    @classmethod
    def activate_laser_powerup(self):
        self.image = self.activated
        laser_interval = 500

    @classmethod
    def deactivate_laser_powerup(self):
        self.image = self.deactivated
        self.laser_interval = 1000


class Spaceship_Powerup(Powerups):
    def __init__(self, normal_image, activated_img, pos):
        super().__init__(normal_image, activated_img, pos)

    def activate_spaceship_powerup(self):
        self.image = self.activated
        spaceship_grp.sprite.bubble_powerup()

    def deactivate_spaceship_powerup(self):
        self.image = self.deactivated


class Meteor_Powerup(Powerups):
    def __init__(self, normal_image, activated_img, pos):
        super().__init__(normal_image, activated_img, pos)

    def activate_spaceship_powerup(self):
        self.image = self.activated
        meteor_grp.y_speed -= 5

    def deactivate_spaceship_powerup(self):
        self.image = self.deactivated
        meteor_grp.y_speed += 5


powerup1 = Laser_Powerup("powerup1.png", (10+10, 70),
                         "./powerup1_activated.png")
powerup2 = Spaceship_Powerup(
    "powerup2.png", (60+10, 70), "./powerup2_activated.png")
powerup3 = Meteor_Powerup("powerup3.png", (110+10, 70),
                          "./powerup3_activated.png")


laser_grp = pygame.sprite.Group()

spaceship = SpaceShip(
    "spaceship.png", "spaceship_charged.png", "spaceship_bubbled.png", 100, 100
)
spaceship_grp = pygame.sprite.GroupSingle()
spaceship_grp.add(spaceship)


meteor_grp = pygame.sprite.Group()
meteor_event = pygame.USEREVENT
time_event = pygame.USEREVENT + 1
laser_event = pygame.USEREVENT + 2
laser_fire = False
laser_timer = 0
meteor_time = 250


# ? pygame.time.set_timer(<Event to trigger>,<time in milliseconds after which it has to be triggered>)
pygame.time.set_timer(meteor_event, meteor_time)
pygame.time.set_timer(time_event, 5000)


def show_fps():
    font = pygame.font.Font("./Pixellari.ttf", 20)
    font_render = font.render(
        f"{int(clock.get_fps())}", 1, pygame.Color("white"))
    screen.blit(font_render, (0, s_height - font_render.get_height()))


def meteor_gen():
    meteor_img = choice(("meteor1.png", "meteor2.png", "meteor3.png"))
    x_pos = randrange(50, 1230)
    y_pos = randrange(-150, -50)
    x_speed = randrange(0, 2)
    y_speed = randrange(7, 12)
    meteor = Meteor(meteor_img, x_pos, y_pos, x_speed, y_speed)
    meteor_grp.add(meteor)


def main_logic():
    global laser_fire
    if pygame.sprite.spritecollide(spaceship_grp.sprite, meteor_grp, dokill=True):
        spaceship_grp.sprite.damage()
        meteor_hit.play()
    if pygame.sprite.groupcollide(laser_grp, meteor_grp, True, True):
        spaceship_grp.sprite.meteors_destroyed += 1

    laser_grp.draw(screen)
    spaceship_grp.draw(screen)
    laser_grp.update()
    spaceship_grp.update()
    meteor_grp.draw(screen)
    meteor_grp.update()
    powerup_grp.draw(screen)
    powerup1.show_on_screen()
    powerup2.show_on_screen()
    powerup3.show_on_screen()
    # time between laser shots
    if pygame.time.get_ticks() - laser_timer >= laser_interval:
        laser_fire = True
        spaceship_grp.sprite.charger()
    return 1


def end_game():
    if spaceship_grp.sprite.health <= 0:
        font = pygame.font.Font("LazenbyCompLiquid.ttf", 50)
        font_render = font.render("Game Over", 1, pygame.Color("white"))
        font_rect = font_render.get_rect(center=(s_width / 2, s_height / 2))
        screen.blit(font_render, font_rect)
        font2 = pygame.font.Font("LazenbyCompLiquid.ttf", 40)
        font_render2 = font2.render(
            f"Score: {score}", 1, pygame.Color("white"))
        font_rect2 = font_render2.get_rect(
            center=(s_width / 2, s_height / 2 + font_render.get_height())
        )
        screen.blit(font_render2, font_rect2)
        font3 = pygame.font.Font("LazenbyCompLiquid.ttf", 20)
        font_render3 = font3.render(
            f"Meteors Destroyed: {spaceship_grp.sprite.meteors_destroyed}",
            1,
            pygame.Color("white"),
        )
        font_rect3 = font_render3.get_rect(
            center=(
                s_width / 2,
                s_height / 2 + font_render2.get_height() + font_render.get_height(),
            )
        )
        screen.blit(font_render3, font_rect3)


run = True
while run:
    screen.fill(background)
    clock.tick(fps)
    if spaceship_grp.sprite.health > 0:
        score += main_logic()
    else:
        end_game()
    # show_fps()

    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            run = False
            sys.exit()
        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_q:
                run = False
                sys.exit()
            if events.key == pygame.K_b:
                spaceship_grp.sprite.bubble_powerup()
            if events.key == pygame.K_l:
                powerup1.activate_laser_powerup()
        if events.type == meteor_event:
            meteor_gen()
        # increasing difficulty
        if events.type == time_event:
            meteor_time -= 5
        if meteor_time <= 170:
            meteor_time = 170
        if events.type == pygame.MOUSEBUTTONDOWN and laser_fire:
            laser = Laser("Laser.png", events.pos)
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

    pygame.display.update()
    print(laser_interval)
