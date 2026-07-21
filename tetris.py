#아직 설치가 안된부품 
#cmd 
#pip install pygame
import random
import sys
from dataclasses import dataclass

import pygame


# Grid settings
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
PLAY_WIDTH = GRID_WIDTH * CELL_SIZE
PLAY_HEIGHT = GRID_HEIGHT * CELL_SIZE
SIDE_PANEL = 220
SCREEN_WIDTH = PLAY_WIDTH + SIDE_PANEL
SCREEN_HEIGHT = PLAY_HEIGHT
FPS = 60

# Colors
BLACK = (18, 18, 18)
WHITE = (245, 245, 245)
GRAY = (55, 55, 55)
CYAN = (0, 220, 220)
BLUE = (60, 100, 240)
ORANGE = (240, 150, 50)
YELLOW = (240, 220, 70)
GREEN = (90, 220, 110)
PURPLE = (170, 90, 220)
RED = (230, 70, 70)

SHAPES = {
    "I": {
        "color": CYAN,
        "rotations": [
            [(0, 1), (1, 1), (2, 1), (3, 1)],
            [(2, 0), (2, 1), (2, 2), (2, 3)],
        ],
    },
    "O": {
        "color": YELLOW,
        "rotations": [
            [(1, 0), (2, 0), (1, 1), (2, 1)],
        ],
    },
    "T": {
        "color": PURPLE,
        "rotations": [
            [(1, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (1, 1), (2, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (1, 2)],
            [(1, 0), (0, 1), (1, 1), (1, 2)],
        ],
    },
    "S": {
        "color": GREEN,
        "rotations": [
            [(1, 0), (2, 0), (0, 1), (1, 1)],
            [(1, 0), (1, 1), (2, 1), (2, 2)],
        ],
    },
    "Z": {
        "color": RED,
        "rotations": [
            [(0, 0), (1, 0), (1, 1), (2, 1)],
            [(2, 0), (1, 1), (2, 1), (1, 2)],
        ],
    },
    "J": {
        "color": BLUE,
        "rotations": [
            [(0, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (2, 0), (1, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (2, 2)],
            [(1, 0), (1, 1), (0, 2), (1, 2)],
        ],
    },
    "L": {
        "color": ORANGE,
        "rotations": [
            [(2, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (1, 1), (1, 2), (2, 2)],
            [(0, 1), (1, 1), (2, 1), (0, 2)],
            [(0, 0), (1, 0), (1, 1), (1, 2)],
        ],
    },
}


@dataclass
class Piece:
    shape_name: str
    x: int = 3
    y: int = 0
    rotation: int = 0

    @property
    def color(self):
        return SHAPES[self.shape_name]["color"]

    @property
    def blocks(self):
        rotations = SHAPES[self.shape_name]["rotations"]
        return rotations[self.rotation % len(rotations)]

    def rotated(self):
        return Piece(self.shape_name, self.x, self.y, self.rotation + 1)


class Tetris:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Python Tetris")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("consolas", 36, bold=True)
        self.ui_font = pygame.font.SysFont("consolas", 24)
        self.small_font = pygame.font.SysFont("consolas", 18)

        self.board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current = self._new_piece()
        self.next_piece = self._new_piece()

        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False

        self.fall_timer = 0.0

    def _new_piece(self):
        return Piece(random.choice(list(SHAPES.keys())), x=3, y=0, rotation=0)

    def _speed(self):
        # Level increases speed; minimum cap prevents impossible frame dependence.
        return max(0.08, 0.7 - (self.level - 1) * 0.06)

    def _valid(self, piece):
        for bx, by in piece.blocks:
            x = piece.x + bx
            y = piece.y + by

            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.board[y][x] is not None:
                return False
        return True

    def _lock_piece(self):
        for bx, by in self.current.blocks:
            x = self.current.x + bx
            y = self.current.y + by
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                self.board[y][x] = self.current.color

        cleared = self._clear_lines()
        if cleared > 0:
            self.lines += cleared
            self.score += [0, 100, 300, 500, 800][cleared] * self.level
            self.level = 1 + self.lines // 10

        self.current = self.next_piece
        self.current.x = 3
        self.current.y = 0
        self.current.rotation = 0
        self.next_piece = self._new_piece()

        if not self._valid(self.current):
            self.game_over = True

    def _clear_lines(self):
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        cleared = GRID_HEIGHT - len(new_board)
        for _ in range(cleared):
            new_board.insert(0, [None for _ in range(GRID_WIDTH)])
        self.board = new_board
        return cleared

    def _move(self, dx, dy):
        moved = Piece(self.current.shape_name, self.current.x + dx, self.current.y + dy, self.current.rotation)
        if self._valid(moved):
            self.current = moved
            return True
        return False

    def _rotate(self):
        rotated = self.current.rotated()
        if self._valid(rotated):
            self.current = rotated
            return

        # Simple wall kick
        for kick in (-1, 1, -2, 2):
            kicked = Piece(rotated.shape_name, rotated.x + kick, rotated.y, rotated.rotation)
            if self._valid(kicked):
                self.current = kicked
                return

    def _hard_drop(self):
        while self._move(0, 1):
            self.score += 2
        self._lock_piece()

    def _soft_drop(self):
        if self._move(0, 1):
            self.score += 1
        else:
            self._lock_piece()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.__init__()
                    return

                if event.key == pygame.K_LEFT:
                    self._move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self._move(1, 0)
                elif event.key == pygame.K_DOWN:
                    self._soft_drop()
                elif event.key == pygame.K_UP:
                    self._rotate()
                elif event.key == pygame.K_SPACE:
                    self._hard_drop()

    def _update(self, dt):
        if self.game_over:
            return

        self.fall_timer += dt
        if self.fall_timer >= self._speed():
            self.fall_timer = 0
            if not self._move(0, 1):
                self._lock_piece()

    def _draw_grid(self):
        self.screen.fill(BLACK)

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.board[y][x]
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if cell is not None:
                    pygame.draw.rect(self.screen, cell, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                else:
                    pygame.draw.rect(self.screen, GRAY, rect, 1)

        for bx, by in self.current.blocks:
            x = self.current.x + bx
            y = self.current.y + by
            if y >= 0:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, self.current.color, rect)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

        # Side panel
        panel_x = PLAY_WIDTH + 12
        pygame.draw.line(self.screen, WHITE, (PLAY_WIDTH, 0), (PLAY_WIDTH, PLAY_HEIGHT), 2)

        title = self.title_font.render("TETRIS", True, WHITE)
        self.screen.blit(title, (panel_x, 20))

        score_text = self.ui_font.render(f"Score: {self.score}", True, WHITE)
        lines_text = self.ui_font.render(f"Lines: {self.lines}", True, WHITE)
        level_text = self.ui_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(score_text, (panel_x, 90))
        self.screen.blit(lines_text, (panel_x, 125))
        self.screen.blit(level_text, (panel_x, 160))

        next_text = self.ui_font.render("Next", True, WHITE)
        self.screen.blit(next_text, (panel_x, 220))

        preview_origin_x = panel_x + 20
        preview_origin_y = 260
        for bx, by in self.next_piece.blocks:
            rect = pygame.Rect(
                preview_origin_x + bx * CELL_SIZE,
                preview_origin_y + by * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(self.screen, self.next_piece.color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 1)

        controls = [
            "[Left/Right] Move",
            "[Down] Soft Drop",
            "[Up] Rotate",
            "[Space] Hard Drop",
        ]
        y = 430
        for line in controls:
            txt = self.small_font.render(line, True, WHITE)
            self.screen.blit(txt, (panel_x, y))
            y += 24

        if self.game_over:
            overlay = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.screen.blit(overlay, (0, 0))

            go = self.title_font.render("GAME OVER", True, WHITE)
            restart = self.ui_font.render("Press R to restart", True, WHITE)
            self.screen.blit(go, (PLAY_WIDTH // 2 - go.get_width() // 2, PLAY_HEIGHT // 2 - 40))
            self.screen.blit(restart, (PLAY_WIDTH // 2 - restart.get_width() // 2, PLAY_HEIGHT // 2 + 5))

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_input()
            self._update(dt)
            self._draw_grid()


if __name__ == "__main__":
    game = Tetris()
    game.run()
