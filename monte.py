import pygame
from pygame.locals import *
import random
import numpy as np
class RobotGame:
    def __init__(self, width, height, obstacle_percent, start, goal, random_state, delay):
        self.width = width
        self.height = height
        self.max_step = width+height-2
        self.obstacle_percent = obstacle_percent
        self.start = start
        self.goal = goal
        self.delay = delay
        pygame.init()
        self.screen_width = 700 
        self.cell_size = self.screen_width // max(width, height)  
        self.screen_height = self.cell_size * max(width, height)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Robot Game")

        self.current_scenario_info = ""

        self.arrow_scale = self.cell_size / 30.0  
        self.arrow_up = pygame.image.load("arrow_up.png")  
        self.arrow_down = pygame.image.load("arrow_down.png")  
        self.arrow_left = pygame.image.load("arrow_left.png")  
        self.arrow_right = pygame.image.load("arrow_right.png")  
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
        self.random_state = random_state
        self.robot_direction = self.arrow_up  # Initial direction

    def generate_random_field(self):
        field = np.zeros((self.height, self.width), dtype=bool)
        num_obstacles = int(self.width * self.height * self.obstacle_percent)

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

        start_x, start_y = self.start
        goal_x, goal_y = self.goal
        pygame.draw.rect(self.screen, (0, 255, 0), (start_x * self.cell_size, start_y * self.cell_size, self.cell_size, self.cell_size))
        pygame.draw.rect(self.screen, (0, 0, 255), (goal_x * self.cell_size, goal_y * self.cell_size, self.cell_size, self.cell_size))

    def draw_robot(self):
        self.screen.blit(self.robot_direction, (self.robot_x * self.cell_size, self.robot_y * self.cell_size))

    def get_possible_moves(self): #Фильтрация ходов так как робот не может двигаться вне поля
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)] #down up right left 
        
        # Дополнительные условия для робота в нижнем левом углу
        if self.robot_x == 0 and self.robot_y == self.height - 1:
            print('Нижний левый угол')
            possible_moves.remove((0, 1))  # Убираем движение вниз
            possible_moves.remove((-1, 0))  # Убираем движение влево

        # Дополнительные условия для робота в верхнем левом углу
        elif self.robot_x == 0 and self.robot_y == 0:
            print('Верхний левый угол')

            possible_moves.remove((0, -1))  # Убираем движение вверх
            possible_moves.remove((-1, 0))  # Убираем движение влево

        # Дополнительные условия для робота в верхнем правом углу
        elif self.robot_x == self.width - 1 and self.robot_y == 0:
            print('Верхний правый угол')
            possible_moves.remove((0, -1))  # Убираем движение вверх
            possible_moves.remove((1, 0))  # Убираем движение направо


        elif self.robot_y == 0:  # Робот в самом верху
            print('Робот сверхууу')
            possible_moves.remove((0, -1))
        elif self.robot_y == self.height - 1:  # Робот в самом низу
            possible_moves.remove((0, 1))
        elif self.robot_x == 0:  # Робот в самой левой стороне
            print('Робот слеваа')
            possible_moves.remove((-1, 0))
        elif self.robot_x == self.width - 1:  # Робот в самой правой стороне
            possible_moves.remove((1, 0))
        
        return possible_moves

    def reset(self): #Рестарт. Начала нового эпизода
        self.current_scenario_info = f"Ep.{self.episode - 1}. Finished: {self.status}. Moves: {self.moves_count}"
        self.episode += 1
        self.robot_x, self.robot_y = self.start
        self.moves_count = 0
        self.moves = [(0, 0)]
        self.status = None

        self.static_info = f"Ep.{self.episode - 1}. Finished: {self.status}. Moves: {self.moves_count}"
    
    def generate_incremental_values(self, count):
        return np.arange(count) / 10.0 

    def update_significances(self):
        point = 10
        self.significances[self.height-1][self.width-1] = 1000000 #финиш имеет максимальное кол-во очков важности
        unique_moves = []  
        for move in self.moves:
            if move not in unique_moves:
                unique_moves.append(move)
        coef = point / len(unique_moves)
        
        if self.status: #если дошел до финиша
            for u in range(len(unique_moves)):
                self.significances[unique_moves[u][1]][unique_moves[u][0]] += point
        else: #если не дошел до финиша
            obstacle_y, obstacle_x = self.moves[-1]
            print('Препятствие:', obstacle_x, obstacle_y)
            self.significances[obstacle_x][obstacle_y] = -1000000
 
            #Оценка важности для пути
            for u in range(len(unique_moves)):
                self.significances[unique_moves[u][1]][unique_moves[u][0]] -= point 
        return self.significances
    def update_significances_old(self):
        max_point = 10
        min_point = -10
        self.significances[self.height-1][self.width-1] = 1000000 #финиш имеет максимальное кол-во очков важности
        if self.status: #если дошел до финиша
            unique_moves = []  
            for move in self.moves:
                if move not in unique_moves:
                    unique_moves.append(move)
            coef2 = max_point / len(unique_moves)
            for u in range(len(unique_moves)):
                self.significances[unique_moves[u][1]][unique_moves[u][0]] += round(u * coef2, 2)
        else: #если не дошел до финиша
            coef = min_point / self.max_step #100/18=5.55
            obstacle_y, obstacle_x = self.moves[-1]
            print('OBSTACLE', obstacle_x, obstacle_y)
            self.significances[obstacle_x][obstacle_y] = -1000000

            #оценка важности методом горячей зоны
            for i in range(self.height):
                for j in range(self.width):
                    if (i==self.width-1 and j==self.height-1) :
                        continue 
                    else:
                        num_steps = abs(obstacle_y-j)+abs(obstacle_x-i)
                        self.significances[i][j] += (self.max_step-num_steps) * coef 
                        self.significances[i][j] = round(self.significances[i][j], 1)
            unique_values = {}
            #одинаковые значения
            for i in range(self.significances.shape[0]):
                for j in range(self.significances.shape[1]):
                    value = self.significances[i, j]
                    if value in unique_values:
                        unique_values[value] += 1
                        # Generate incremental values for this occurrence
                        incremental_values = self.generate_incremental_values(unique_values[value])
                        self.significances[i, j] = round(value + incremental_values[-1], 1)
                    else:
                        unique_values[value] = 1


        return self.significances

    def encrypt_moves(self, possible_moves): #Направления для дебаггинга
        encrypted_moves = []
        for i in possible_moves:
            if i == (0, 1):
                encrypted_moves.append('B')
            elif i == (0, -1):
                encrypted_moves.append('T')
            elif i == (1, 0):
                encrypted_moves.append('R')
            elif i == (-1, 0):
                encrypted_moves.append('L')
        return encrypted_moves
   
    def move_robot(self):
        possible_moves = self.get_possible_moves()
        encrypted_moves = self.encrypt_moves(possible_moves)

        #Случайный выбор хода
        if random.random() < self.random_state:
            best_move = random.choice(possible_moves)
            print(f'Robot:[{self.robot_x, self.robot_y}]. Poss. moves:{encrypted_moves}, Rand. choosen:{best_move}.\n')
        else:
            possible_signs = []
            for possible_move in possible_moves:
                temp_x = self.robot_x + possible_move[0]
                temp_y = self.robot_y + possible_move[1]
                possible_signs.append(self.significances[temp_y][temp_x])
            
            max_value = max(possible_signs)
            max_indices = np.where(np.array(possible_signs) == max_value)[0]

            # Избегаем возврата на предыдущий ход
            if len(self.moves) > 1:
                for i in max_indices:
                    if self.robot_x+possible_moves[i][0] != self.moves[-1][0] and self.robot_y+possible_moves[i][1] != self.moves[-1][1]:
                        chosen_index = i

            chosen_index = random.choice(max_indices) if len(max_indices) > 1 else max_indices[0]
            best_move = possible_moves[chosen_index]
            print(f'Robot:[{self.robot_x, self.robot_y}]. Poss. moves:{encrypted_moves}, Poss.signs:{possible_signs}, Choosen:{best_move}.\n')
        
        new_x = self.robot_x + best_move[0]
        new_y = self.robot_y + best_move[1] 

        if (0 <= new_x < self.width) and (0 <= new_y < self.height):
            self.robot_x = new_x
            self.robot_y = new_y

            if best_move == (0, 1):
                self.robot_direction = self.arrow_down
            elif best_move == (0, -1):
                self.robot_direction = self.arrow_up
            elif best_move == (1, 0):
                self.robot_direction = self.arrow_right
            elif best_move == (-1, 0):
                self.robot_direction = self.arrow_left
        return (new_x, new_y)
    
    def info(self):
        for i in range(self.height):
            for j in range(self.width):
                print(self.significances[i][j], end=' ')
            print()

        return f'Ep.{self.episode}. Finished:{self.status}. {self.moves_count} moves. \n{self.moves}\n'

    def render_text(self):
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.current_scenario_info, True, (0, 0, 255))
        return text_surface


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
                self.running = False
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


            text_surface = self.render_text()
            self.screen.blit(text_surface, (10, 10))

            pygame.display.flip()
            pygame.time.delay(self.delay)

        pygame.quit()

if __name__ == "__main__":
    width, height = 15,15 
    obstacle_percent = 0.2  # Процент заполнения препятствиями
    start = (0, 0)
    goal = (width-1, height-1)
    random_state = 0.1
    delay = 10
    game = RobotGame(width, height, obstacle_percent, start, goal, random_state, delay)
    game.run_game()