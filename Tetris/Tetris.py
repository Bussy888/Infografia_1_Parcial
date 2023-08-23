import os
import random

import arcade

SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Tetris"

GRID_SIZE = 30

SHAPES = [
    [[1, 1, 0],
     [0, 1, 1]],

    [[0, 1, 1],
     [1, 1, 0]],

    [[1, 1, 1, 1]],

    [[1, 1],
     [1, 1]],

    [[1, 0, 0],
     [1, 1, 1]],

    [[0, 0, 1],
     [1, 1, 1]],

    [[0, 1, 0],
     [1, 1, 1]],
]


class TetrisGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.grid = [[0] * (SCREEN_WIDTH // GRID_SIZE) for _ in range(SCREEN_HEIGHT // GRID_SIZE)]
        self.current_shape = None
        self.current_shape_x = 0
        self.current_shape_y = 0

        self.score = 0

        self.spawn_new_shape()

        self.update_timer = 0
        self.update_interval = 0.3

        self.game_over = False

        self.score = 0
        self.game_over = False

        sonido = arcade.load_sound("assets/tetris_song.mp3")
        self.background_music = arcade.Sound("assets/ghost.mp3")
        self.background_music_player = None

    def draw_grid(self):
        for row in range(len(self.grid)):
            for column in range(len(self.grid[row])):
                if self.grid[row][column] == 1:
                    arcade.draw_rectangle_filled(column * GRID_SIZE + GRID_SIZE / 2,
                                                 row * GRID_SIZE + GRID_SIZE / 2,
                                                 GRID_SIZE, GRID_SIZE, arcade.color.GREEN)
                    arcade.draw_rectangle_outline(column * GRID_SIZE + GRID_SIZE / 2,
                                                  row * GRID_SIZE + GRID_SIZE / 2, GRID_SIZE, GRID_SIZE,
                                                  arcade.color.BLUE_GREEN)

    def draw_shape(self):
        for row in range(len(self.current_shape)):
            for col in range(len(self.current_shape[row])):
                if self.current_shape[row][col]:
                    x = (self.current_shape_x + col) * GRID_SIZE + GRID_SIZE / 2
                    y = (self.current_shape_y - row) * GRID_SIZE + GRID_SIZE / 2
                    arcade.draw_rectangle_filled(x, y, GRID_SIZE, GRID_SIZE, arcade.color.GREEN)
                    arcade.draw_rectangle_outline(x, y, GRID_SIZE, GRID_SIZE, arcade.color.BLUE_GREEN)

    def spawn_new_shape(self):
        if self.current_shape_y >= len(self.grid) - len(self.current_shape) if self.current_shape else 0:
            self.game_over = True
            return
        self.current_shape = random.choice(SHAPES)  # Selecciona una figura aleatoria
        self.current_shape_x = len(self.grid[0]) // 2
        self.current_shape_y = len(self.grid)

    def move_shape_down(self):
        self.current_shape_y -= 1

    def rotate_shape(self):
        new_shape = []
        for col in range(len(self.current_shape[0])):
            new_row = []
            for row in range(len(self.current_shape) - 1, -1, -1):
                new_row.append(self.current_shape[row][col])
            new_shape.append(new_row)
        if not self.check_collision(self.current_shape_x, self.current_shape_y, new_shape):
            self.current_shape = new_shape

    def check_collision(self, x, y, shape):
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    grid_row = y - row
                    grid_col = x + col

                    # Colisiones
                    if (
                            grid_col < 0 or
                            grid_col >= len(self.grid[0])
                    ):
                        return True

                    if (
                            grid_row < 0 or
                            grid_col < 0 or
                            grid_row >= len(self.grid) or
                            self.grid[grid_row][grid_col]
                    ):
                        return True
        return False

    def remove_completed_lines(self):
        completed_lines = []
        for row in range(len(self.grid)):
            if all(self.grid[row]):
                completed_lines.append(row)

        for row in completed_lines:
            self.grid.pop(row)
            self.grid.insert(0, [0] * (SCREEN_WIDTH // GRID_SIZE))

        # Mover Abajo
        for row in range(len(self.grid)):
            if row < len(self.grid) - len(completed_lines):
                for col in range(len(self.grid[row])):
                    self.grid[row][col] = self.grid[row + len(completed_lines)][col]
        self.score += len(completed_lines) * 100

    def restart_game(self):
        self.grid = [[0] * (SCREEN_WIDTH // GRID_SIZE) for _ in range(SCREEN_HEIGHT // GRID_SIZE)]
        self.current_shape = None
        self.current_shape_x = 0
        self.current_shape_y = 0
        self.score = 0
        self.game_over = False
        self.spawn_new_shape()

    def update(self, delta_time):
        if self.game_over:
            return

        # Temporizador
        self.update_timer += delta_time

        # Actualizar Temp
        if self.update_timer >= self.update_interval:
            self.update_timer = 0  # Reinicia el temporizador

            if not self.check_collision(self.current_shape_x, self.current_shape_y - 1, self.current_shape):
                self.move_shape_down()
            else:
                for row in range(len(self.current_shape)):
                    for col in range(len(self.current_shape[row])):
                        if self.current_shape[row][col]:
                            grid_row = self.current_shape_y - row
                            grid_col = self.current_shape_x + col

                            if grid_row < 0:
                                self.game_over = True
                                return

                            self.grid[grid_row][grid_col] = 1
                self.remove_completed_lines()
                self.spawn_new_shape()

    def on_show(self):
        self.background_music_player = self.background_music.play(volume=0.5, loop=True)

    def on_hide(self):
        if self.background_music_player:
            self.background_music_player.stop()
            self.background_music_player = None
    def on_draw(self):
        arcade.start_render()

        self.draw_grid()
        self.draw_shape()

        if self.game_over:
            arcade.draw_text("Game Over", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.RED, font_size=30, anchor_x="center")
            arcade.draw_text("Pulse 'R' para Reiniciar", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                             arcade.color.WHITE, font_size=20, anchor_x="center")

        # Score
        arcade.draw_text(f"Score: {self.score}", 10, 10, arcade.color.RED, font_size=16)

    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.R:
                self.restart_game()
        else:
            if key == arcade.key.LEFT:
                if not self.check_collision(self.current_shape_x - 1, self.current_shape_y, self.current_shape):
                    self.current_shape_x -= 1
            elif key == arcade.key.RIGHT:
                if not self.check_collision(self.current_shape_x + 1, self.current_shape_y, self.current_shape):
                    self.current_shape_x += 1
            elif key == arcade.key.DOWN:
                if not self.check_collision(self.current_shape_x, self.current_shape_y - 1, self.current_shape):
                    self.move_shape_down()
            elif key == arcade.key.UP:
                self.rotate_shape()


def main():
    game = TetrisGame()
    arcade.run()


if __name__ == "__main__":
    main()
