import numpy as np
import pygame


class Robot_and_wall:
    def __init__(self, size, p_wall):
        self.size = size
        self.state_space_size = size**2
        self.action_space_size = 4  # Вверх, Вниз, Влево, Вправо
        self.p_wall = p_wall  # Вероятность наличия дырок
        self.start = (0, 0)
        self.goal = (size - 1, size - 1)
        self.walls = self.generate_walls()
        self.current_state = self.start
        self.episode_number = 0
        self.hit_count = 0
        self.previous_state = None

        # Инициализация Pygame
        self.screen_size = 600
        self.cell_size = self.screen_size // size
        self.colors = {'player': (0, 0, 255), 'goal': (255, 0, 0), 'wall': (0, 0, 0), 'path': (255, 255, 255)}
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))

    def generate_walls(self):
        walls = []
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) != self.start and (i, j) != self.goal and np.random.rand() < self.p_wall:
                    walls.append((i, j))
        return walls

    def draw_grid(self):
        self.screen.fill((255, 255, 255))
        for i in range(self.size):
            for j in range(self.size):
                rect = pygame.Rect(j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_cell(self, position, color):
        rect = pygame.Rect(position[1] * self.cell_size, position[0] * self.cell_size, self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, color, rect)

    def visualize(self, state, action):
        self.draw_grid()

        # Отрисовка состояния
        self.draw_cell(self.goal, self.colors['goal'])
        self.draw_cell(self.current_state, self.colors['player'])
        for wall in self.walls:
            self.draw_cell(wall, self.colors['wall'])

        font = pygame.font.SysFont(None, 30)
        text = font.render(f'Episode: {self.episode_number}', True, (1, 0, 0))
        text1 = font.render(f'Hit count: {self.hit_count}', True, (1, 0, 0))

        # Отображение text слева
        self.screen.blit(text, (10, self.screen_size - 40))

        # Отображение text1 справа
        text1_width, text1_height = font.size(f'Hit count: {self.hit_count}')
        self.screen.blit(text1, (self.screen_size - 10 - text1_width, self.screen_size - 40))

        pygame.display.flip()

        # Задержка для визуализации
        pygame.time.delay(10)
    def close(self):
        pygame.quit()

    def reset(self):
        self.current_state = self.start
        self.previous_state = None
        self.episode_number += 1  # Увеличиваем номер эпизода
        self.hit_count = 0
        return self.current_state

    def step(self, action):
        x, y = self.get_next_state(self.current_state, action)
        reward = -1

        if (x, y) == self.goal:
            if x in range(self.goal[0] - 3, self.goal[0] + 4) and y in range(self.goal[1] - 3, self.goal[1] + 4):
                reward = 10  # Дополнительное вознаграждение, если агент в зоне вокруг финиша
            else:
                reward = 1  # Базовое вознаграждение за достижение финиша
            done = True
        elif (x, y) in self.walls:
            reward = -10
            self.hit_count+=1
            done = False
            print("Agent hit a wall, returning to the previous state.")
            x, y = self.current_state
        else:
                done = False
        self.current_state = (x, y)

        return self.current_state, reward, done

    def get_next_state(self, state, action):
        x, y = state
        if action == 0:
            x = max(0, x - 1)
        elif action == 1:
            x = min(self.size - 1, x + 1)
        elif action == 2:
            y = max(0, y - 1)
        elif action == 3:
            y = min(self.size - 1, y + 1)
        return x, y


def epsilon_greedy_policy(Q_state, epsilon):
    if np.random.rand() < epsilon:
        return np.random.choice(len(Q_state))
    else:
        return np.argmax(Q_state)


def initialize_q(num_states, num_actions):
    return np.zeros((num_states, num_actions))
def find_optimal_episode(episode_steps):
    if len(episode_steps)>1:
        min_steps = min(episode_steps)
        optimal_episode = episode_steps.index(min_steps) + 1  # Добавляем 1, так как индексы начинаются с 0
        return optimal_episode, min_steps
#  alpha: Скорость обучения (learning rate).
                                                                                                                #  gamma: Дисконт-фактор, влияющий на важность будущих вознаграждений.
                                                                                                                #  epsilon: Параметр для стратегии выбора действий (ε-жадная).
def sarsa(env, num_episodes, alpha, gamma, epsilon):
    num_states = env.state_space_size
    num_actions = env.action_space_size
    Q = initialize_q(num_states, num_actions)

    episode_steps = []  # Для сохранения количества шагов за каждый эпизод

    for episode in range(num_episodes):
        state = env.reset()
        action = epsilon_greedy_policy(Q[state[0] * env.size + state[1]], epsilon)
        steps = 0  # Счетчик шагов

        while True:
            env.visualize(state, action)  # Визуализация

            next_state, reward, done = env.step(action)
            next_action = epsilon_greedy_policy(Q[next_state[0] * env.size + next_state[1]], epsilon)

            Q[state[0] * env.size + state[1]][action] += alpha * (
                    reward + gamma * Q[next_state[0] * env.size + next_state[1]][next_action] - Q[state[0] * env.size + state[1]][action])

            state = next_state
            action = next_action

            steps += 1

            if done:
                print(f"Episode {episode + 1} finished after {steps} steps.")
                if state == env.goal:
                    print("Agent reached the GOOOOAAAAALLL!\n")
                else:
                    print("Agent did not reach the goal.\n")

                episode_steps.append(steps)  # Сохраняем количество шагов текущего эпизода
                break
    if len(episode_steps)>1:
                optimal_episode, min_steps = find_optimal_episode(episode_steps)
                print(f"Optimal episode: {optimal_episode}, Min steps: {min_steps}")

    env.close()
    return Q, episode_steps

def main():
    env = Robot_and_wall(size=25, p_wall=0.2)
    num_episodes = 500
    alpha = 0.1
    gamma = 0.9
    epsilon = 0.01
    Q_values, steps_per_episode = sarsa(env, num_episodes, alpha, gamma, epsilon)
    pygame.init()

if __name__ == "__main__":
    main()