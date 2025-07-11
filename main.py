import pygame
import sys
import random
from game_objects import PlayerBar, BounceBall, WallBlock, BonusItem, SafetyNet, LaserBeam

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

screen_w, screen_h = 850, 650
screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption("Arkanoid by Zafar Abdullayev")

BG_COLOR = pygame.Color('grey12')
BLOCK_COLORS = [(178, 34, 34), (255, 165, 0), (255, 215, 0), (50, 205, 50)]
font = pygame.font.Font(None, 40)

# === Sounds ===
try:
    bounce_snd = pygame.mixer.Sound('bounce.wav')
    brick_snd = pygame.mixer.Sound('brick_break.wav')
    fail_snd = pygame.mixer.Sound('game_over.wav')
    laser_snd = pygame.mixer.Sound('laser.wav')
except:
    class Silent:
        def play(self): pass

    bounce_snd = brick_snd = fail_snd = laser_snd = Silent()

# === Game Setup ===
player = PlayerBar(screen_w, screen_h)
balls = [BounceBall(screen_w, screen_h)]
blocks = []
bonuses = []
beams = []
net = None

score = 0
lives = 3
level = 0
mute = False

def generate_blocks(rows):
    grid = []
    cols = 10
    bw, bh = 75, 20
    pad = 5
    top_y = 50
    for r in range(rows):
        for c in range(cols):
            x = c * (bw + pad) + pad
            y = r * (bh + pad) + top_y
            color = BLOCK_COLORS[r % len(BLOCK_COLORS)]
            grid.append(WallBlock(x, y, bw, bh, color))
    return grid

levels = [1, 2, 3]
blocks = generate_blocks(levels[level])

state = 'title'

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                if state == 'title':
                    state = 'playing'
                elif state == 'game_over':
                    player.restart()
                    balls = [BounceBall(screen_w, screen_h)]
                    level = 0
                    blocks = generate_blocks(levels[level])
                    score = 0
                    lives = 3
                    bonuses.clear()
                    beams.clear()
                    net = None
                    state = 'title'
            if e.key == pygame.K_r and state == 'game_over':
                player.restart()
                balls = [BounceBall(screen_w, screen_h)]
                level = 0
                blocks = generate_blocks(levels[level])
                score = 0
                lives = 3
                bonuses.clear()
                beams.clear()
                net = None
                state = 'playing'
            if e.key == pygame.K_m:
                mute = not mute
            if e.key == pygame.K_f and player.can_shoot:
                beams.append(LaserBeam(player.rect.centerx - 30, player.rect.top))
                beams.append(LaserBeam(player.rect.centerx + 30, player.rect.top))
                if not mute:
                    laser_snd.play()

    screen.fill(BG_COLOR)

    if state == 'title':
        screen.blit(font.render("ARKANOID", True, (255, 255, 255)), (screen_w//2 - 140, 180))
        screen.blit(font.render("Press SPACE to Start", True, (255, 255, 255)), (screen_w//2 - 150, 250))
        screen.blit(font.render("Press M to Mute", True, (255, 255, 255)), (screen_w//2 - 120, 300))

    elif state == 'playing':
        player.handle_input()
        player.render(screen)

        for ball in balls[:]:
            result = ball.move(player)
            ball.render(screen)
            if result == 'lost':
                if net and net.visible:
                    ball.rect.bottom = net.rect.top
                    ball.velocity_y *= -1
                    net.visible = False
                else:
                    balls.remove(ball)
                    if not balls:
                        lives -= 1
                        if not mute:
                            fail_snd.play()
                        if lives <= 0:
                            state = 'game_over'
                        else:
                            balls = [BounceBall(screen_w, screen_h)]
                            player.restart()

        for block in blocks[:]:
            for ball in balls:
                if ball.rect.colliderect(block.rect):
                    if not ball.is_burning:
                        ball.velocity_y *= -1
                    if not mute:
                        bounce_snd.play()
                    blocks.remove(block)
                    score += 10
                    if random.random() < 0.3:
                        kind = random.choice(['expand', 'clone', 'barrier', 'flame', 'blaster'])
                        bonuses.append(BonusItem(block.rect.centerx, block.rect.centery, kind))
                    break
            block.render(screen)

        for b in bonuses[:]:
            b.update()
            b.render(screen)
            if player.rect.colliderect(b.rect):
                if b.kind == 'expand':
                    player.width = 150
                    player.rect.width = player.width
                elif b.kind == 'clone':
                    new_ball = BounceBall(screen_w, screen_h)
                    new_ball.rect.center = balls[0].rect.center
                    new_ball.velocity_x = -balls[0].velocity_x
                    new_ball.velocity_y = balls[0].velocity_y
                    balls.append(new_ball)
                elif b.kind == 'barrier':
                    net = SafetyNet(screen_w, screen_h - 10)
                elif b.kind == 'flame':
                    for ball in balls:
                        ball.is_burning = True
                elif b.kind == 'blaster':
                    player.can_shoot = True
                bonuses.remove(b)

        for beam in beams[:]:
            beam.update()
            if beam.rect.bottom < 0:
                beams.remove(beam)
            else:
                for block in blocks[:]:
                    if beam.rect.colliderect(block.rect):
                        blocks.remove(block)
                        if not mute:
                            brick_snd.play()
                        score += 10
                        beams.remove(beam)
                        break
            beam.render(screen)

        if net:
            net.render(screen)

        if not blocks:
            level += 1
            if level < len(levels):
                blocks = generate_blocks(levels[level])
                balls = [BounceBall(screen_w, screen_h)]
                player.restart()
            else:
                level = 0
                blocks = generate_blocks(levels[level])
                balls = [BounceBall(screen_w, screen_h)]
                player.restart()

        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Lives: {lives}", True, (255, 255, 255)), (screen_w - 120, 10))

    elif state == 'game_over':
        screen.blit(font.render("GAME OVER", True, (255, 0, 0)), (screen_w//2 - 100, 240))
        screen.blit(font.render("Press R to Retry", True, (255, 255, 255)), (screen_w//2 - 120, 300))

    pygame.display.flip()
    clock.tick(60)