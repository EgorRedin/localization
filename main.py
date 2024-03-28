import pygame
import random
import numpy as np

pHit = 0.95
pMiss = 0.05
senseError = 1


# возвращает координаты наиболее вероятного значения
def argmax(values):
    len_y = len(values)
    len_x = len(values[0])
    p_row = []
    for i in values: p_row.extend(i)

    num_max = max(enumerate(p_row), key=lambda x: x[1])[0]
    y = num_max // len_x
    x = num_max % len_x

    return x, y


# изменяет матрицу вероятности при поступлении информации с датчика
def sence(p, z, random_map):
    len_y = len(p)
    len_x = len(p[0])

    p_new = []

    for i in range(len_y):
        p_new.append([])
        for j in range(len_x):
            hit = (z == random_map[i][j])
            p_new[i].append(p[i][j] * (hit * pHit + (1 - hit) * pMiss))

    s = 0

    for i in p_new:
        s += sum(i)

    p_new = [[round(p_new[i][j] / s, 4) for j in range(len_x)] for i in range(len_y)]

    return p_new


# изменяет матрицу вероятности при движении
p_Exact = 0.8
p_Over = 0.1
p_Under = 0.1


def move_up(p, u):
    len_y = len(p)
    len_x = len(p[0])
    p_new = []

    for i in range(len_y):
        p_new.append([])
        for j in range(len_x):
            s = p_Exact * p[(i + u) % len_y][j]
            s += p_Over * p[(i + u + 1) % len_y][j]
            s += p_Under * p[(i + u - 1) % len_y][j]

            p_new[i].append(round(s, 4))

    return p_new


def move_down(p, u):
    len_y = len(p)
    len_x = len(p[0])
    p_new = []

    for i in range(len_y):
        p_new.append([])
        for j in range(len_x):
            s = p_Exact * p[(i - u) % len_y][j]
            s += p_Over * p[(i - u + 1) % len_y][j]
            s += p_Under * p[(i - u - 1) % len_y][j]

            p_new[i].append(round(s, 4))

    return p_new


def move_left(p, u):
    len_y = len(p)
    len_x = len(p[0])
    p_new = []

    for i in range(len_y):
        p_new.append([])
        for j in range(len_x):
            s = p_Exact * p[i][(j + u) % len_x]
            s += p_Over * p[i][(j + u + 1) % len_x]
            s += p_Under * p[i][(j + u - 1) % len_x]

            p_new[i].append(round(s, 4))

    return p_new


def move_right(p, u):
    len_y = len(p)
    len_x = len(p[0])
    p_new = []

    for i in range(len_y):
        p_new.append([])
        for j in range(len_x):
            s = p_Exact * p[i][(j - u) % len_x]
            s += p_Over * p[i][(j - u + 1) % len_x]
            s += p_Under * p[i][(j - u - 1) % len_x]

            p_new[i].append(round(s, 4))

    return p_new


pygame.init()

falseCounter = 0

# Параметры экрана
ROBOT_WIDTH = 400
ROBOT_HEIGHT = 400
SCREEN_HEIGHT = 500
SCREEN_WIDTH = 800
FPS = 15

# Цвета
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (192, 192, 192)

# Размеры ячеек на карте
CELL_SIZE = 40


# Класс робота
class Robot(pygame.sprite.Sprite):
    def __init__(self, pos, grid):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(WHITE)
        pygame.draw.circle(self.image, (0, 0, 255), (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2)
        self.rect = self.image.get_rect()
        self.grid = grid
        self.pos = pos
        self.rect.topleft = self.grid_to_pixel(self.pos)

    def update(self):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            global p
            global falseCounter
            new_pos = (self.pos[0] - 1 if self.pos[0] - 1 != -1 else len(self.grid) - 1, self.pos[1])

            #             if self.valid_move(new_pos):
            self.pos = new_pos
            self.rect.topleft = self.grid_to_pixel(self.pos)
            p = move_left(p, 1)
            if random.random() <= senseError:
                p = sence(p, self.grid[self.pos[1]][self.pos[0]], self.grid)
            else:
                p = sence(p, not self.grid[self.pos[1]][self.pos[0]], self.grid)

            if argmax(p) != self.pos:
                falseCounter += 1

        if keys[pygame.K_RIGHT]:

            new_pos = (self.pos[0] + 1 if self.pos[0] + 1 != len(self.grid) else 0, self.pos[1])

            self.pos = new_pos
            self.rect.topleft = self.grid_to_pixel(self.pos)
            p = move_right(p, 1)

            if random.random() <= senseError:
                p = sence(p, self.grid[self.pos[1]][self.pos[0]], self.grid)
            else:
                p = sence(p, not self.grid[self.pos[1]][self.pos[0]], self.grid)

            if argmax(p) != self.pos:
                falseCounter += 1

        if keys[pygame.K_UP]:

            new_pos = (self.pos[0], self.pos[1] - 1 if self.pos[1] - 1 != -1 else len(self.grid) - 1)

            self.pos = new_pos
            self.rect.topleft = self.grid_to_pixel(self.pos)
            p = move_up(p, 1)
            if random.random() <= senseError:
                p = sence(p, self.grid[self.pos[1]][self.pos[0]], self.grid)
            else:
                p = sence(p, not self.grid[self.pos[1]][self.pos[0]], self.grid)

            if argmax(p) != self.pos:
                falseCounter += 1

        if keys[pygame.K_DOWN]:
            new_pos = (self.pos[0], self.pos[1] + 1 if self.pos[1] + 1 != len(self.grid) else 0)
            self.pos = new_pos
            self.rect.topleft = self.grid_to_pixel(self.pos)
            p = move_down(p, 1)
            if random.random() <= senseError:
                p = sence(p, self.grid[self.pos[1]][self.pos[0]], self.grid)
            else:
                p = sence(p, not self.grid[self.pos[1]][self.pos[0]], self.grid)

            if argmax(p) != self.pos:
                falseCounter += 1

    def grid_to_pixel(self, pos):
        return pos[0] * CELL_SIZE, pos[1] * CELL_SIZE


# Функция для создания случайной карты мира
def generate_random_map(width, height, obstacle_probability):
    grid = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            if random.random() < obstacle_probability:
                grid[y][x] = 1
    return grid


FONT_SIZE = 16

p = np.zeros((ROBOT_WIDTH // CELL_SIZE, ROBOT_HEIGHT // CELL_SIZE))


# Функция для запуска
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Среда моделирования для робота")
    clock = pygame.time.Clock()
    # Генерация случайной карты мира
    random_map = generate_random_map(ROBOT_WIDTH // CELL_SIZE, ROBOT_HEIGHT // CELL_SIZE, 0.2)

    # Начальная позиция робота
    robot_pos = (random.randint(0, len(random_map[0]) - 1), random.randint(0, len(random_map) - 1))

    # матрица вероятности
    global p
    global senseError
    p[robot_pos[1]][robot_pos[0]] = 1

    # Перерасчет матрицы вероятности при попадании на случайную клетку
    p = sence(p, random_map[robot_pos[1]][robot_pos[0]], random_map)

    # Создание робота
    robot = Robot(robot_pos, random_map)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(robot)
    font = pygame.font.Font(None, FONT_SIZE)
    active = False
    user_text = str(senseError)
    name_rect = pygame.Rect(0, 440, 100, 100)
    input_rect = pygame.Rect(200, 425, 100, 60)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
            if event.type == pygame.KEYDOWN:
                if active:
                    tmp = user_text
                    if event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                        if user_text:
                            senseError = float(user_text)
                    elif event.key in [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4,
                                       pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9,
                                       pygame.K_PERIOD, pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                       pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        if len(user_text) < 5:
                            user_text += event.unicode
                            if user_text:
                                senseError = float(user_text)
        screen.fill(WHITE)
        # Отображение карты мира
        for y in range(len(random_map)):
            for x in range(len(random_map[0])):
                color = GRAY
                if random_map[y][x] == 0:
                    color = GREEN
                elif random_map[y][x] == 1:
                    color = RED
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        for y in range(len(p)):
            for x in range(len(p[0])):
                pygame.draw.rect(screen, WHITE, (x * CELL_SIZE + 400, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                # Отображаем значение в центре клетки
                text = font.render(str(p[y][x]), True, BLACK)
                text_rect = text.get_rect(
                    center=((x * CELL_SIZE + CELL_SIZE // 2) + 400, y * CELL_SIZE + CELL_SIZE //
                            2))
                screen.blit(text, text_rect)

        text_counter = font.render(f"False count: {falseCounter}", True, BLACK)
        text_counter_rect = text_counter.get_rect(
            center=(50, CELL_SIZE // 2)
        )
        screen.blit(text_counter, text_counter_rect)
        # Обновление и отображение робота
        all_sprites.update()
        all_sprites.draw(screen)
        if active:
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)
        pygame.draw.rect(screen, color, input_rect, 2)
        pygame.draw.rect(screen, WHITE, name_rect)
        font_error = pygame.font.Font(None, 32)
        text_surface = font_error.render("Sensor Error:", True, BLACK)
        screen.blit(text_surface, name_rect)
        text_surface = font_error.render(user_text, True, BLACK)
        screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))
        input_rect.w = max(100, text_surface.get_width() + 10)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
