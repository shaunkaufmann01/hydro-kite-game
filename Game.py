import pygame
import HydroSim as hs
import numpy as np
import os
import pygame


from pygame.locals import (
    K_LEFT,
    K_RIGHT,

)
""" first time building a game so this wont be pretty"""


def rot_center(image, rect, angle):
    """rotate an image while keeping its center"""
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect


class HydroSprite(pygame.sprite.Sprite):
    """
        hydro-kite sprite for game, uses sim for physics
    """

    # -- Methods
    def __init__(self, cen_rot_x, cen_rot_y):
        super().__init__()

        #  load and prep image
        self.image = pygame.image.load(os.path.join('Kite.png'))
        self.rect = self.image.get_rect()
        rx, ry = self.rect .center
        self.rect.x = -rx
        self.rect.y = -ry

        self.cen_rot_x = cen_rot_x
        self.cen_rot_y = cen_rot_y

        self.orig_rect = self.rect  # orig used for rotation
        self.orig_image = self.image

        # sprite locations stuff
        self.tether_radius = 330  # pixels

        # pitch
        self.beta = 0.001
        self.beta_lim = (85/180)*np.pi
        self.theta = 0.001

        #  for keys
        self.pressed_keys = []
        self.control_add = (4 / 180) * np.pi

        #  hydro sim vars

        # stability stuff
        self.dt = 0.0001
        self.time_distortion = 1.3
        self.substep = 4  # increases stability
        self.smoothfactor_dt = 0.1

        #  hydro sim setup
        water = hs.FluidProp()
        tether = hs.Tether(unloaded_length=30)
        craft = hs.TempCraft(fluidprop=water)
        craft.mass = 30
        self.physics = hs.TempSystem(craft, tether)
        self.physics.theta = self.theta

    def control(self, pressed_keys):
        self.pressed_keys = pressed_keys
        if pressed_keys[K_LEFT]:
            self.beta = self.beta - self.control_add
        elif pressed_keys[K_RIGHT]:
            self.beta = self.beta + self.control_add

        # limit angle
        if self.beta > self.beta_lim:
            self.beta = self.beta_lim
        elif self.beta < -self.beta_lim:
            self.beta = -self.beta_lim

        # update beta in simulation
        self.physics.beta = self.beta

    def update(self):
        # step forward in time of hydro_sim
        dt_old = self.dt
        self.dt = self.smoothfactor_dt * (1 - self.smoothfactor_dt) + dt_old * self.smoothfactor_dt  # smooth time steps
        self.dt = self.dt*self.time_distortion
        for i in range(self.substep):  # use sub steping to improve stability
            self.physics.step_time(self.dt/self.substep)

        self.theta = self.physics.theta  # update game theta based on sim theta

        # change sprite image location and rotation
        angle = 180 * (self.theta - self.beta) / np.pi
        self.image, self.rect = rot_center(self.orig_image, self.orig_rect, angle)
        self.rect.x = self.rect.x + self.tether_radius*np.sin(self.theta) + self.cen_rot_x
        self.rect.y = self.rect.y + self.tether_radius*np.cos(self.theta) + self.cen_rot_y


class Tether(pygame.sprite.Sprite):
    """
        hydro-kite sprite
    """
    # -- Methods
    def __init__(self,cen_rot_x, cen_rot_y):
        super().__init__()
        #  load and prep image
        self.image = pygame.image.load(os.path.join('tether_eng2.png'))
        self.rect = self.image.get_rect()
        rx, ry = self.rect .center

        self.rect.x = -rx
        self.rect.y = -ry

        self.rect.x = self.rect.x + cen_rot_x
        self.rect.y = self.rect.y + cen_rot_y

        self.orig_rect = self.rect  # orig used for rotation
        self.orig_image = self.image
        self.theta = 0

    def update(self):
        angle = 180 * self.theta / np.pi
        self.image, self.rect = rot_center(self.orig_image, self.orig_rect, angle)


class BackGround:
    def __init__(self):
        self.image = pygame.image.load(os.path.join('Background3.png'))
        self.rect = self.image.get_rect()
        self.rect.x = self.rect.x-10
    def blitz(self):
        screen.blit(self.image, self.rect)


class GameScore:
    def __init__(self, screen):
        #  load and prep image
        self.screen = screen
        self.current_power = 0
        self.power_pos = (0, 0)
        self.power_pos_avg = (370, 0)
        self.power_counter = 0
        self.update_counter = 0
        self.power_run_avg = 0
        self.reduce_update = 5
        self.v_stream = 1.5
        self.font = pygame.font.SysFont('arial', 30)
        self.current_power_surface = self.font.render(str(self.current_power), False, (255, 255, 255))
        self.avg_power_surface = self.font.render(str(round(self.power_run_avg)) + ' Watts', False, (255, 255, 255))
        self.river_pos = (100+150, 100)
        self.river_surface = self.font.render('River velocity = 1.5 m/s', False, (255, 255, 255))



    def update(self, power):
        self.power_run_avg = (self.power_run_avg * self.power_counter + power) / (self.power_counter + 1)
        self.power_counter = self.power_counter + 1

        if self.update_counter > self.reduce_update:
            self.current_power = power
            self.update_counter = 0
        else:
            self.update_counter = self.update_counter + 1

    def blitz(self):
        self.current_power_surface = self.font.render('Power: current ' + str(round(self.current_power)) + ' W', False, (255, 255, 255))
        self.screen.blit(self.current_power_surface, self.power_pos)
        self.avg_power_surface = self.font.render('run-avg ' + str(round(self.power_run_avg)) + ' W', False, (255, 255, 255))
        self.screen.blit(self.avg_power_surface, self.power_pos_avg)

        self.river_surface = self.font.render('River velocity = 1.5 m/s', False, (255, 255, 255))
        self.screen.blit(self.river_surface, self.river_pos)

#  RUN GAME
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1190
SCREEN_HEIGHT = 900

# Set the height and width of the screen
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("TidalGame")
pygame.font.init()  # you have to call this at the start,

# instantiate sprite
cen_rot_x = 613
cen_rot_y = 325
hydrokite = HydroSprite(cen_rot_x, cen_rot_y)
tether = Tether(cen_rot_x, cen_rot_y)

# instantiate game score board
scoreboard = GameScore(screen)
shiftx = 255
scoreboard.power_pos = (0 + shiftx, 0)
scoreboard.power_pos_avg = (370 + shiftx, 0)

# instantiate background
background = BackGround()

END = False
# Used game time
clock = pygame.time.Clock()
dt = 17/1000

pygame.key.set_repeat(13)
# MAIN GAME LOOP
while not END:
    tic = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print('Quiting')
            END = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print('Quiting')
                END = True

    screen.fill(pygame.Color("skyblue"))

    #  UPDATE SPRITES
    pressed_keys = pygame.key.get_pressed()
    hydrokite.control(pressed_keys)
    hydrokite.dt = dt
    hydrokite.update()
    tether.theta = hydrokite.theta
    tether.update()

    # Text
    scoreboard.update(hydrokite.physics.power)

    # blitz
    background.blitz()
    scoreboard.blitz()
    screen.blit(tether.image, tether.rect)
    screen.blit(hydrokite.image, hydrokite.rect)

    # Limit to 60 frames per seconds and update time step
    clock.tick(60)
    toc = pygame.time.get_ticks()
    dt = (toc-tic)/1000

    #update the screen .
    pygame.display.flip()

# exit.
pygame.quit()