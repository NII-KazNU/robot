import random
import matplotlib.pyplot as plt
import numpy as np

class Robot_and_wall:
    def __init__(self, size, slip_prob):
        self.size = size
        self.slip_prob = slip_prob
        self.player_pos = (0, 0)
        self.goal_pos = (size-1,size-1)
        self.wall_pos = []
        self.done = False
        self.steps = 0
        self.generate_random_walls()
        self.returned_to_start = False  # Флаг для отслеживания возвращения на стартовую позицию
        self.successful_way = []  # Список для хранения координат успешных путей
        self.unique_routes = {}

        # Включаем интерактивный режим
        plt.ion()

    def reset(self):
        self.player_pos = (0, 0)
        self.done = False
        self.steps = 0
        self.returned_to_start = False  # Сбрасываем флаг при каждом новом эпизоде
        self.successful_way = []
        return self.player_pos

    def move(self, action):
        if action == 0:  # Left
            new_pos = (self.player_pos[0], max(0, self.player_pos[1] - 1))
        elif action == 1:  # Down
            new_pos = (min(self.player_pos[0] + 1, self.size - 1), self.player_pos[1])
        elif action == 2:  # Right
            new_pos = (self.player_pos[0], min(self.player_pos[1] + 1, self.size - 1))
        elif action == 3:  # Up
            new_pos = (max(0, self.player_pos[0] - 1), self.player_pos[1])

        # Slippery ice
        if random.uniform(0, 1) < self.slip_prob:
            new_pos = self.random_move()

        self.player_pos = new_pos
        self.steps += 1

        self.successful_way.append(tuple(self.player_pos))

        # Check if the game is done
        if self.player_pos == self.goal_pos:
            self.done = True
            self.returned_to_start = True
            reward = 1.0  # Дополнительная награда за достижение цели

            if tuple(self.successful_way) not in self.unique_routes:
                self.unique_routes[tuple(self.successful_way)] = 1
            else:
                self.unique_routes[tuple(self.successful_way)] += 1

        elif self.player_pos in self.wall_pos:
            self.done = True
            reward = -1.0  # Отрицательная награда за попадание в препятствие
        else:
            reward = 0.1  # Базовая награда за каждый шаг

        return self.player_pos, reward, self.done

    def random_move(self):
        return random.choice([(self.player_pos[0], max(0, self.player_pos[1] - 1)),
                               (min(self.player_pos[0] + 1, self.size - 1), self.player_pos[1]),
                               (self.player_pos[0], min(self.player_pos[1] + 1, self.size - 1)),
                               (max(0, self.player_pos[0] - 1), self.player_pos[1])])

    def generate_random_walls(self):
        # Randomly determine the number of holes
        num_walls = random.randint(1, (self.size**2) // 4)  # One hole for every 4 cells

        # Randomly generate hole positions
        self.wall_pos = []
        while len(self.wall_pos) < num_walls:
            wall = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
            if wall != self.goal_pos and wall not in self.wall_pos:
                self.wall_pos.append(wall)

    def visualize(self):
        # Create an array for visualization
        grid = np.ones((self.size, self.size, 3))  # White background

        # Set colors
        grid[self.player_pos[0], self.player_pos[1]] = [0, 0, 1]  # Blue for player
        grid[self.goal_pos[0], self.goal_pos[1]] = [1, 0, 0]  # Red for goal

        for wall_pos in self.wall_pos:
            grid[wall_pos[0], wall_pos[1]] = [0, 0, 0]  # Black for hole

        # Print reward
        reward_str = f"Reward: {self.steps * 0.1:.2f}"  # Use the total steps multiplied by the base reward
        plt.text(0, -0.5, reward_str, fontsize=12)

        # Visualize the grid using matplotlib
        plt.imshow(grid, interpolation='nearest', aspect='equal')
        plt.xticks(range(0, self.size, 10))  # Adjust ticks for better readability
        plt.yticks(range(0, self.size, 10))  # Adjust ticks for better readability
        plt.title(f"Step number: {self.steps}\n")
        plt.draw()  # Обновляем текущее изображение
        plt.pause(0.01)  # Ждем некоторое время, чтобы дать шанс обновиться

        # Очищаем текущий текст
        plt.clf()

# Example usage with visualization:
if __name__ == "__main__":
    unique_routes = []  # Словарь для сохранения уникальных маршрутов
    robot_wall = Robot_and_wall(size=10, slip_prob=0.2)
    min_steps_to_goal = float('inf')

    for i in range(100):
        state = robot_wall.reset()
        done = False

        while not done:
            action = random.randint(0, 3)
            new_state, reward, done = robot_wall.move(action)
            robot_wall.visualize()
        if done and state == robot_wall.goal_pos and not robot_wall.returned_to_start:
            print(f"{i} Minimum steps to goal: {robot_wall.steps}")

        if done:
            if state == robot_wall.goal_pos:
                print(f"{i} Success! The goal is reached in {robot_wall.steps} steps.\n")
            else:
                print(f"{i} Episode finished after {robot_wall.steps} steps\n")

    print(f"Number of unique routes: {len(robot_wall.unique_routes)}")
    print("All unique routes:")
    for way in robot_wall.unique_routes.items():
            print(f"Route: {way}")
# Выключаем интерактивный режим после завершения
plt.ioff()
plt.show()