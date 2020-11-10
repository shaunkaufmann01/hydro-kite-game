import pygame
from Sprites import HydroSprite
from Sprites import Tether
from Sprites import GameScore
from Sprites import BackGround
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
background = BackGround(screen)

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