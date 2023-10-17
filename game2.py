import pygame
import random
import numpy as np
from pygame.locals import *

class RobotGame:
    def __init__(self, width, height, obstacle_percent, start, goal):
        self.width = width
        self.height = height
        self.max_step = width+height-2
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
    
        self.field = self.generate_random_field()
        self.significances = np.zeros((self.height, self.width), dtype=np.float64)
        self.robot_x, self.robot_y = start
        self.running = True

        self.moves_count = 0
        self.episode = 1
        self.status = None
        self.moves = [(0, 0)]

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

    def get_possible_moves(self):
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        if self.robot_y == 0:  # Робот в самом верху
            possible_moves.remove((-1, 0))
        elif self.robot_y == self.height - 1:  # Робот в самом низу
            possible_moves.remove((1, 0))
        elif self.robot_x == 0:  # Робот в самой левой стороне
            possible_moves.remove((0, -1))
        elif self.robot_x == self.width - 1:  # Робот в самой правой стороне
            possible_moves.remove((0, 1))
            
        # Дополнительные условия для робота в нижнем левом углу
        elif self.robot_x == 0 and self.robot_y == self.height - 1:
            possible_moves.remove((-1, 0))  # Убираем движение вниз
            possible_moves.remove((0, -1))  # Убираем движение влево

        # Дополнительные условия для робота в вверхнем правом углу
        elif self.robot_x == self.width - 1 and self.robot_y == 0:
            possible_moves.remove((1, 0))  # Убираем движение вверх
            possible_moves.remove((0, 1))  # Убираем движение направо

        # Дополнительные условия для робота в вверхнем левом углу
        elif self.robot_x == self.width - 1 and self.robot_y == 0:
            possible_moves.remove((1, 0))  # Убираем движение вверх
            possible_moves.remove((0, -1))  # Убираем движение влево

        return possible_moves

    def reset(self):
        self.episode += 1
        self.robot_x, self.robot_y = self.start
        self.moves_count = 0
        self.moves = [(0, 0)]
        self.status = None
        

    def update_significances(self):
        max_point = 100
        min_point = -100
        self.significances[self.height-1][self.width-1] = 100 #финиш имеет 100 очков важности
        if self.status: #если дошел до финиша
            pass
        else: #если не дошел до финиша
            coef = min_point / self.max_step #100/18=5.55
            obstacle_y, obstacle_x = self.moves[-1]
            self.significances[obstacle_x][obstacle_y] = min_point
            for i in range(self.height):
                for j in range(self.width):
                    if (i == 0 and j == 0) or (i==self.width-1 and j==self.height-1) :
                        continue 
                    else:
                        num_steps = abs(obstacle_y-j)+abs(obstacle_x-i)
                        self.significances[i][j] += num_steps * coef


        return self.significances
    def move_robot(self):
        random_move = random.choice(self.get_possible_moves())
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
        return (new_x, new_y)
    
    def info(self):
        return f'Ep.{self.episode}. {self.moves_count} moves. \n{self.moves}\n{self.significances}'

    def run_game(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

            self.screen.fill((255, 255, 255))
            self.draw_field()
            self.draw_robot()
            self.moves.append(self.move_robot())
            self.moves_count += 1

            if (self.robot_x, self.robot_y) == self.goal:
                # self.running = False
                self.status = True
                self.update_significances()
                print(self.info())
                self.reset()

            # Добавьте проверку на столкновение с препятствием
            if self.field[self.robot_y, self.robot_x]:
                # self.running = False
                self.status = False
                self.significances = self.update_significances()
                print(self.info())
                self.reset()

            pygame.display.flip()
            pygame.time.delay(100)

        pygame.quit()

if __name__ == "__main__":
    width, height = 10, 10
    obstacle_percent = 4  # Процент заполнения препятствиями
    start = (0, 0)
    goal = (width-1, height-1)

    game = RobotGame(width, height, obstacle_percent, start, goal)
    game.run_game()
