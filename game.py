import pygame
import random
import numpy as np
from pygame.locals import *

class RobotGame:
    def __init__(self, width, height, obstacle_percent, start, goal):
        self.width = width
        self.height = height
        self.obstacle_percent = obstacle_percent
        self.start = start
        self.goal = goal

        pygame.init()
        self.screen_width = 700  # Фиксированный размер окна
        self.cell_size = self.screen_width // max(width, height)  # Динамический размер ячейки
        self.screen_height = self.cell_size * max(width, height)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Robot Game")

        # Динамический размер стрелок
        self.arrow_scale = self.cell_size / 30.0  # Стандартный размер стрелок - 30 пикселей
        self.arrow_up = pygame.image.load("arrow_up.png")  # Replace with your arrow image file
        self.arrow_down = pygame.image.load("arrow_down.png")  # Replace with your arrow image file
        self.arrow_left = pygame.image.load("arrow_left.png")  # Replace with your arrow image file
        self.arrow_right = pygame.image.load("arrow_right.png")  # Replace with your arrow image file
        self.arrow_up = pygame.transform.scale(self.arrow_up, (int(30 * self.arrow_scale), int(30 * self.arrow_scale)))
        self.arrow_down = pygame.transform.scale(self.arrow_down, (int(30 * self.arrow_scale), int(30 * self.arrow_scale)))
        self.arrow_left = pygame.transform.scale(self.arrow_left, (int(30 * self.arrow_scale), int(30 * self.arrow_scale)))
        self.arrow_right = pygame.transform.scale(self.arrow_right, (int(30 * self.arrow_scale), int(30 * self.arrow_scale)))
        
        self.scenarios = []  # Список для хранения путей и количества ходов
        self.moves = []  # Список для хранения информации о каждом движении
        self.move_count = 0  # Счетчик ходов
        
        self.field = self.generate_random_field()
        self.robot_x, self.robot_y = start
        self.running = True

        self.robot_direction = self.arrow_up  # Initial direction

    def generate_random_field(self):
        field = np.zeros((self.height, self.width), dtype=bool)
        num_obstacles = int(self.width * self.height * self.obstacle_percent / 100)

        for _ in range(num_obstacles):
            while True:
                x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
                if not field[y, x]:
                    field[y, x] = True
                    break

        return field

    def draw_field(self):
        for x in range(self.width):
            for y in range(self.height):
                color = (0, 0, 0) if self.field[y, x] else (255, 255, 255)
                pygame.draw.rect(self.screen, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, (0, 0, 0), (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size), 1)

        # Draw the start and finish points
        start_x, start_y = self.start
        goal_x, goal_y = self.goal
        pygame.draw.rect(self.screen, (0, 255, 0), (start_x * self.cell_size, start_y * self.cell_size, self.cell_size, self.cell_size))
        pygame.draw.rect(self.screen, (0, 0, 255), (goal_x * self.cell_size, goal_y * self.cell_size, self.cell_size, self.cell_size))

    def draw_robot(self):
        self.screen.blit(self.robot_direction, (self.robot_x * self.cell_size, self.robot_y * self.cell_size))

    def move_robot(self):
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if self.robot_y == 0: #робот в самом вверху
            possible_moves.remove((-1, 0))
        if self.robot_y == self.height-1: #робот в самом низу
            possible_moves.remove((1, 0)) 
        if self.robot_x == 0: #робот в самой левой стороне
            possible_moves.remove((0, -1))
        if self.robot_x == self.width-1: #робот в самой правой стороне
            possible_moves.remove((0, 1))
        print(possible_moves)
        random_move = random.choice(possible_moves)
        new_x = self.robot_x + random_move[0]
        new_y = self.robot_y + random_move[1]

        if (0 <= new_x < self.width) and (0 <= new_y < self.height):
            self.robot_x = new_x
            self.robot_y = new_y

            # Update robot direction based on movement
            if random_move == (0, 1):
                self.robot_direction = self.arrow_down
            elif random_move == (0, -1):
                self.robot_direction = self.arrow_up
            elif random_move == (1, 0):
                self.robot_direction = self.arrow_right
            elif random_move == (-1, 0):
                self.robot_direction = self.arrow_left


    def restart_game(self):
        self.robot_x, self.robot_y = self.start
        self.running = True
        self.moves = []  # Сбрасываем информацию о движении
        self.move_count = 0
    
    def get_scenarios(self):
        return self.scenarios
    
    def run_game(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    
            # Запоминаем текущее положение робота
            current_position = (self.robot_x, self.robot_y)
            
            self.screen.fill((255, 255, 255))
            self.draw_field()
            self.draw_robot()
            self.move_robot()
            # Добавляем информацию о текущем движении
            self.moves.append(current_position)
            # Добавьте проверку на столкновение с препятствием
            if self.field[self.robot_y, self.robot_x]:
                scenario = (list(self.moves), self.move_count)  # Добавляем путь и количество ходов
                self.scenarios.append(scenario)
                self.restart_game()  # Перезапустите игру при столкновении

            # Проверяем условия завершения сценария
            if (self.robot_x, self.robot_y) == self.goal:
                scenario = (list(self.moves), self.move_count)  # Добавляем путь и количество ходов
                self.scenarios.append(scenario)
                self.running = False

            # Добавьте проверку на выход за границы игрового поля
            if not (0 <= self.robot_x < self.width) or not (0 <= self.robot_y < self.height):
                scenario = (list(self.moves), self.move_count)  # Добавляем путь и количество ходов
                self.scenarios.append(scenario)
                self.restart_game()  # Перезапустите игру при выходе за границы поля

           

            # Увеличиваем счетчик ходов
            self.move_count += 1

            pygame.display.flip()
            pygame.time.delay(200)

        # После завершения сценария, запустите новую игру с начальной точки
        self.restart_game()


    def get_unique_paths_count(self):
        return len(self.paths)
if __name__ == "__main__":
    width, height = 10, 10
    obstacle_percent = 10  # Процент заполнения препятствиями
    start = (0, 0)
    goal = (width-1, height-1)

    game = RobotGame(width, height, obstacle_percent, start, goal)
    game.run_game()

    # Вывод информации о сценариях и количестве ходов
    scenarios = game.get_scenarios()

    for i, (path, move_count) in enumerate(scenarios, start=1):
        print(f"Сценарий {i}:")
        print(f"Путь: {path}")
        print(f"Количество ходов: {move_count}")
        print()