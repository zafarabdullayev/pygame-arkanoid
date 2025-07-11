import pygame
import random

pygame.font.init()
BONUS_FONT = pygame.font.Font(None, 20)

class PlayerBar:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.default_width = 100
        self.height = 10
        self.move_speed = 7
        self.color = (180, 220, 255)

        self.width = self.default_width
        self.rect = pygame.Rect(
            self.screen_w // 2 - self.width // 2,
            self.screen_h - 30,
            self.width,
            self.height
        )
        self.can_shoot = False

    def restart(self):
        self.rect.x = self.screen_w // 2 - self.default_width // 2
        self.width = self.default_width
        self.rect.width = self.width
        self.can_shoot = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.move_speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.move_speed

        self.rect.x = max(0, min(self.rect.x, self.screen_w - self.rect.width))

    def render(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class BounceBall:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.radius = 10
        self.color = (255, 255, 200)
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.is_burning = False
        self.reset_position()

    def reset_position(self):
        self.rect.center = (self.screen_w // 2, self.screen_h // 2)
        self.velocity_x = 6 * random.choice((1, -1))
        self.velocity_y = -6
        self.is_burning = False

    def move(self, player):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        if self.rect.top <= 0:
            self.velocity_y *= -1
        if self.rect.left <= 0 or self.rect.right >= self.screen_w:
            self.velocity_x *= -1

        if self.rect.colliderect(player.rect) and self.velocity_y > 0:
            offset = (self.rect.centerx - player.rect.centerx) / (player.rect.width // 2)
            self.velocity_x += offset * 5
            self.velocity_y *= -1

        if self.rect.top > self.screen_h:
            return 'lost'
        return 'active'

    def render(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)


class WallBlock:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def render(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class BonusItem:
    TYPES = {
        'expand': {'color': (60, 60, 255), 'symbol': 'E'},
        'clone': {'color': (255, 105, 180), 'symbol': 'C'},
        'barrier': {'color': (0, 255, 255), 'symbol': 'B'},
        'flame': {'color': (255, 69, 0), 'symbol': 'F'},
        'blaster': {'color': (255, 0, 0), 'symbol': 'L'},
    }

    def __init__(self, x, y, kind):
        self.width = 30
        self.height = 15
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.velocity_y = 3
        self.kind = kind
        self.color = self.TYPES[kind]['color']
        self.symbol = self.TYPES[kind]['symbol']

    def update(self):
        self.rect.y += self.velocity_y

    def render(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text = BONUS_FONT.render(self.symbol, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


class SafetyNet:
    def __init__(self, screen_w, y):
        self.rect = pygame.Rect(0, y, screen_w, 10)
        self.visible = True

    def render(self, surface):
        if self.visible:
            pygame.draw.rect(surface, (0, 255, 255), self.rect)


class LaserBeam:
    def __init__(self, x, y):
        self.width = 5
        self.height = 15
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = (255, 255, 0)
        self.velocity_y = -8

    def update(self):
        self.rect.y += self.velocity_y

    def render(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
