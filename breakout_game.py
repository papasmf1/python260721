import random
import sys

import pygame


# Screen settings
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
BLUE = (80, 160, 255)
RED = (255, 100, 100)
GREEN = (90, 220, 140)
YELLOW = (255, 220, 100)
ORANGE = (255, 170, 70)


class Paddle:
    def __init__(self):
        self.width = 360
        self.height = 16
        self.x = (WIDTH - self.width) // 2
        self.y = HEIGHT - 50
        self.speed = 8
        self.shooter_timer = 0
        self.shoot_cooldown = 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        if self.x < 0:
            self.x = 0
        if self.x + self.width > WIDTH:
            self.x = WIDTH - self.width

    def update(self):
        if self.shooter_timer > 0:
            self.shooter_timer -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    @property
    def can_shoot(self):
        return self.shooter_timer > 0 and self.shoot_cooldown == 0

    def activate_shooter(self, duration_frames=600):
        # Extend remaining time when the player gets the same item repeatedly.
        self.shooter_timer = max(self.shooter_timer, duration_frames)

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect, border_radius=8)


class Ball:
    def __init__(self):
        self.radius = 10
        self.reset()

    @property
    def rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2,
        )

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5
        self.vx = random.choice([-1, 1]) * self.speed
        self.vy = -self.speed

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx *= -1
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -1

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)


class Brick:
    def __init__(self, x, y, width, height, color, hp=1):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hp = hp

    @property
    def alive(self):
        return self.hp > 0

    def hit(self):
        self.hp -= 1

    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=6)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=6)


class Item:
    def __init__(self, x, y, item_type="gun"):
        self.item_type = item_type
        self.width = 22
        self.height = 22
        self.x = x - self.width // 2
        self.y = y - self.height // 2
        self.speed = 3

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, ORANGE, self.rect, border_radius=6)
        draw_text(screen, "G", 18, self.x + 5, self.y + 1, BLACK)


class Bullet:
    def __init__(self, x, y):
        self.width = 6
        self.height = 14
        self.x = x - self.width // 2
        self.y = y
        self.speed = 11

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.rect, border_radius=3)


def create_bricks(rows=6, cols=10):
    bricks = []
    padding = 8
    top_margin = 70
    side_margin = 40
    brick_width = (WIDTH - side_margin * 2 - padding * (cols - 1)) // cols
    brick_height = 28

    palette = [RED, YELLOW, GREEN, BLUE]

    for row in range(rows):
        for col in range(cols):
            x = side_margin + col * (brick_width + padding)
            y = top_margin + row * (brick_height + padding)
            color = palette[row % len(palette)]
            hp = 1 if row < 4 else 2
            bricks.append(Brick(x, y, brick_width, brick_height, color, hp))
    return bricks


def handle_ball_paddle_collision(ball, paddle):
    if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
        ball.y = paddle.y - ball.radius
        ball.vy *= -1

        # Change the reflection angle depending on where it hits the paddle.
        hit_pos = (ball.x - paddle.x) / paddle.width  # 0.0 ~ 1.0
        offset = (hit_pos - 0.5) * 2.0  # -1.0 ~ 1.0
        ball.vx = offset * 6

        # Keep a minimum horizontal speed so the game does not become vertical-only.
        if abs(ball.vx) < 2:
            ball.vx = 2 if ball.vx >= 0 else -2


def handle_ball_brick_collision(ball, bricks):
    score_gain = 0
    destroyed_bricks = []
    for brick in bricks:
        if brick.alive and ball.rect.colliderect(brick.rect):
            overlap_left = ball.rect.right - brick.rect.left
            overlap_right = brick.rect.right - ball.rect.left
            overlap_top = ball.rect.bottom - brick.rect.top
            overlap_bottom = brick.rect.bottom - ball.rect.top

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap in (overlap_left, overlap_right):
                ball.vx *= -1
            else:
                ball.vy *= -1

            brick.hit()
            score_gain += 100
            if not brick.alive:
                destroyed_bricks.append(brick)
            break

    return score_gain, destroyed_bricks


def handle_bullet_brick_collision(bullets, bricks):
    score_gain = 0
    destroyed_bricks = []

    for bullet in bullets[:]:
        bullet_hit = False
        for brick in bricks:
            if brick.alive and bullet.rect.colliderect(brick.rect):
                brick.hit()
                score_gain += 120
                if not brick.alive:
                    destroyed_bricks.append(brick)
                bullets.remove(bullet)
                bullet_hit = True
                break
        if bullet_hit:
            continue

    return score_gain, destroyed_bricks


def draw_text(screen, text, size, x, y, color=WHITE, center=False):
    font = pygame.font.SysFont("malgungothic", size)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Breakout Game")
    clock = pygame.time.Clock()

    paddle = Paddle()
    ball = Ball()
    bricks = create_bricks()
    items = []
    bullets = []

    score = 0
    lives = 3
    game_over = False
    game_clear = False

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game_over or game_clear):
                    paddle = Paddle()
                    ball = Ball()
                    bricks = create_bricks()
                    items = []
                    bullets = []
                    score = 0
                    lives = 3
                    game_over = False
                    game_clear = False
                if event.key == pygame.K_SPACE and paddle.can_shoot and not game_over and not game_clear:
                    bullets.append(Bullet(paddle.x + paddle.width // 2, paddle.y - 10))
                    paddle.shoot_cooldown = 10

        keys = pygame.key.get_pressed()
        if not game_over and not game_clear:
            paddle.move(keys)
            paddle.update()
            ball.update()

            for bullet in bullets[:]:
                bullet.update()
                if bullet.y + bullet.height < 0:
                    bullets.remove(bullet)

            for item in items[:]:
                item.update()
                if item.rect.colliderect(paddle.rect):
                    if item.item_type == "gun":
                        paddle.activate_shooter(600)
                    items.remove(item)
                elif item.y > HEIGHT:
                    items.remove(item)

            handle_ball_paddle_collision(ball, paddle)
            ball_score, ball_destroyed = handle_ball_brick_collision(ball, bricks)
            score += ball_score

            bullet_score, bullet_destroyed = handle_bullet_brick_collision(bullets, bricks)
            score += bullet_score

            for destroyed in ball_destroyed + bullet_destroyed:
                if random.random() < 0.25:
                    items.append(Item(destroyed.rect.centerx, destroyed.rect.centery, "gun"))

            if ball.y - ball.radius > HEIGHT:
                lives -= 1
                ball.reset()
                if lives <= 0:
                    game_over = True

            if all(not brick.alive for brick in bricks):
                game_clear = True

        screen.fill(BLACK)

        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)
        for item in items:
            item.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)

        draw_text(screen, f"Score: {score}", 28, 16, 12)
        draw_text(screen, f"Lives: {lives}", 28, WIDTH - 130, 12)
        if paddle.shooter_timer > 0:
            seconds_left = paddle.shooter_timer // FPS
            draw_text(screen, f"Gun: {seconds_left}s", 24, 16, HEIGHT - 34, ORANGE)
            draw_text(screen, "SPACE: Shoot", 24, WIDTH - 180, HEIGHT - 34, YELLOW)

        if game_over:
            draw_text(screen, "GAME OVER", 56, WIDTH // 2, HEIGHT // 2 - 30, RED, center=True)
            draw_text(
                screen,
                "R: Restart  |  ESC: Quit",
                26,
                WIDTH // 2,
                HEIGHT // 2 + 24,
                WHITE,
                center=True,
            )

        if game_clear:
            draw_text(screen, "YOU WIN!", 56, WIDTH // 2, HEIGHT // 2 - 30, GREEN, center=True)
            draw_text(
                screen,
                "R: Restart  |  ESC: Quit",
                26,
                WIDTH // 2,
                HEIGHT // 2 + 24,
                WHITE,
                center=True,
            )

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        pygame.display.flip()


if __name__ == "__main__":
    main()