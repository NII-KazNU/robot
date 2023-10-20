import pygame
from pygame.locals import *
import random
import monte
import sarsa
import markov

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Выбора метода")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BUTTON_COLOR = (60, 100, 200)
HOVER_COLOR = (80, 120, 220)

# Create buttons
font = pygame.font.Font(None, 36)
button_monte = font.render("Monte Carlo", True, WHITE)
button_sarsa = font.render("SARSA", True, WHITE)
button_markov = font.render("Markov", True, WHITE)

button_rect_monte = button_monte.get_rect(center=(200, 100))
button_rect_sarsa = button_sarsa.get_rect(center=(200, 150))
button_rect_markov = button_markov.get_rect(center=(200, 200))

def draw_button(button, rect, color):
    pygame.draw.rect(screen, color, rect)
    screen.blit(button, rect)

# Run the Pygame event loop
method = None
running = True

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            if button_rect_monte.collidepoint(event.pos):
                method = '1'
                running = False
            elif button_rect_sarsa.collidepoint(event.pos):
                method = '2'
                running = False
            elif button_rect_markov.collidepoint(event.pos):
                method = '3'
                running = False

    screen.fill(WHITE)

    # Check if the mouse is over the buttons and change their color accordingly
    if button_rect_monte.collidepoint(pygame.mouse.get_pos()):
        draw_button(button_monte, button_rect_monte, HOVER_COLOR)
    else:
        draw_button(button_monte, button_rect_monte, BUTTON_COLOR)

    if button_rect_sarsa.collidepoint(pygame.mouse.get_pos()):
        draw_button(button_sarsa, button_rect_sarsa, HOVER_COLOR)
    else:
        draw_button(button_sarsa, button_rect_sarsa, BUTTON_COLOR)

    if button_rect_markov.collidepoint(pygame.mouse.get_pos()):
        draw_button(button_markov, button_rect_markov, HOVER_COLOR)
    else:
        draw_button(button_markov, button_rect_markov, BUTTON_COLOR)

    pygame.display.flip()

# Close the Pygame window
pygame.quit()








if method == '1': #Monte
    width, height = 15,15 
    obstacle_percent = 0.2  # Процент заполнения препятствиями
    start = (0, 0)
    goal = (width-1, height-1)
    random_state = 0.1
    delay = 10
    game = monte.RobotGame(width, height, obstacle_percent, start, goal, random_state, delay)
    game.run_game()
elif method == '2':#Sarsa
    env = sarsa.Robot_and_wall(size=25, p_wall=0.2)
    num_episodes = 500
    alpha = 0.1
    gamma = 0.9
    epsilon = 0.01
    Q_values, steps_per_episode = sarsa(env, num_episodes, alpha, gamma, epsilon)
    pygame.init()
elif method == '3':#Markov
    unique_routes = []  # Словарь для сохранения уникальных маршрутов
    robot_wall = markov.Robot_and_wall(size=10, slip_prob=0.2)
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