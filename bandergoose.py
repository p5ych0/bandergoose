import os
import pygame
import random

from itertools import  cycle
from pygame.constants import QUIT, K_UP, K_DOWN, K_LEFT, K_RIGHT, KEYDOWN

pygame.init()

FPS = pygame.time.Clock()

HEIGHT = 800
WIDTH = 1200

TEXT_COLOR = (20, 20, 40)

main_display = pygame.display.set_mode((WIDTH, HEIGHT))
bg = pygame.transform.scale(pygame.image.load('./images/background.png'), (WIDTH, HEIGHT))
bgw = bg.get_width()
bg_move = 2
bg_X1 = 0
bg_X2 = bgw

FONT = pygame.font.SysFont('Verdana', 20)
IMAGE_PATH = './images/player/'
SPRITES = cycle(map(lambda s: IMAGE_PATH + s, os.listdir(IMAGE_PATH)))

player = pygame.image.load(next(SPRITES))
player_rect = pygame.Rect(WIDTH / 5, HEIGHT / 2, *player.get_size())
player_mask = pygame.mask.from_surface(player)
player_speed = 4

score = 0

enemies = []
bonuses = []
animate = []

playing = True

def create_enemy():
    enemy = pygame.transform.scale(pygame.image.load('./images/enemy.png').convert_alpha(), (80, 30))
    enemy_size = enemy.get_size()
    enemy_rect = pygame.Rect(WIDTH, random.randint(enemy_size[0] + 30, HEIGHT - enemy_size[0] - 30), *enemy_size)
    enemy_move = [random.randint(-6, -3), 0]
    enemy_mask = pygame.mask.from_surface(enemy)
    return [enemy, enemy_rect, enemy_move, enemy_mask]

def create_bonus():
    bonus = pygame.transform.scale(pygame.image.load('./images/bonus.png').convert_alpha(), (90, 150))
    bonus_size = bonus.get_size()
    bonus_rect = pygame.Rect(random.randint(bonus_size[0] + 100, WIDTH - bonus_size[0] - 100), -bonus_size[1], *bonus_size)
    bonus_move = [0, random.randint(1, 3)]
    bonus_mask = pygame.mask.from_surface(bonus)
    return [bonus, bonus_rect, bonus_move, bonus_mask, 25]


CREATE_EMEMY = pygame.USEREVENT + 1
CREATE_BONUS = pygame.USEREVENT + 2
ANIMATE = pygame.USEREVENT + 3

pygame.time.set_timer(CREATE_EMEMY, 1300)
pygame.time.set_timer(CREATE_BONUS, 3700)
pygame.time.set_timer(ANIMATE, 200)

while playing:
    FPS.tick(120)

    for event in pygame.event.get():
        if event.type == QUIT:
            playing = False
        if event.type == CREATE_EMEMY:
            enemies.append(create_enemy())
        if event.type == CREATE_BONUS:
            bonuses.append(create_bonus())
        if event.type == ANIMATE:
            player = pygame.image.load(next(SPRITES))
            player_mask = pygame.mask.from_surface(player)

    keys = pygame.key.get_pressed()

    player_rect = player_rect.move([
        player_speed if keys[K_RIGHT] and player_rect.right < WIDTH else -player_speed if keys[K_LEFT] and player_rect.left > 0 else 0,
        player_speed if keys[K_DOWN] and player_rect.bottom < HEIGHT - 30 else -player_speed if keys[K_UP] and player_rect.top > 0 else 0
    ])

    main_display.blit(bg, (bg_X1, 0))
    main_display.blit(bg, (bg_X2, 0))

    bg_X1 -= bg_move
    bg_X2 -= bg_move

    if bg_X2 < 0:
        bg_X1 = 0
        bg_X2 = bgw

    for enemy in enemies:
        if player_rect.colliderect(enemy[1]):
            kaboom = player_mask.overlap(enemy[3], (enemy[1][0] - player_rect.x, enemy[1][1] - player_rect.y))
            if kaboom:
                playing = False
                boom = pygame.transform.scale(pygame.image.load('./images/boom.png').convert_alpha(), (200, 200))
                boom_rect = boom.get_rect()
                boom_rect.center = (player_rect.x + kaboom[0], player_rect.y + kaboom[1])

        enemy[1] = enemy[1].move(enemy[2])

        if enemy[1].right < 0:
            enemies.pop(enemies.index(enemy))
        else:
            main_display.blit(enemy[0], enemy[1])

    for bonus in bonuses:
        bonus[1] = bonus[1].move(bonus[2])

        if bonus[1].top > HEIGHT:
            bonuses.pop(bonuses.index(bonus))
        else:
            if player_rect.colliderect(bonus[1]):
                if player_mask.overlap(bonus[3], (bonus[1][0] - player_rect.x, bonus[1][1] - player_rect.y)):
                    animate.append(bonuses.pop(bonuses.index(bonus)))
                    score += 1
            else:
                main_display.blit(bonus[0], bonus[1])

    main_display.blit(player, player_rect)

    for animation in animate:
        size = animation[1]
        center = size.center
        animation[0] = pygame.transform.smoothscale(animation[0], (size[2] + 8, size[3] + 15))
        pygame.Surface.set_alpha(animation[0], animation[4] * 10)
        animation[1] = animation[0].get_rect()
        animation[1].center = center
        animation[4] -= 1
        main_display.blit(animation[0], animation[1])
        if animation[4] < 1:
            animate.pop(animate.index(animation))

    if playing == False:
        main_display.blit(boom, boom_rect)

    main_display.blit(FONT.render(str(score), True, TEXT_COLOR), (WIDTH - 50, 20))

    pygame.display.flip()

pygame.time.delay(1500)
