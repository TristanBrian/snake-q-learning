import pygame
import numpy as np
import random

# Initialize Pygame
pygame.init()

# Game parameters
width, height = 400, 400
block_size = 20
speed = 10

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# Q-learning parameters
gamma = 0.9           # Discount factor
alpha = 0.1           # Learning rate
epsilon = 1.0         # Exploration rate
epsilon_decay = 0.995 # Decay rate for exploration
min_epsilon = 0.01

# Initialize screen
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Snake Game with Q-Learning')

# Snake and food classes
class Snake:
    def __init__(self):
        self.body = [[100, 50], [90, 50], [80, 50]]
        self.direction = "RIGHT"
    
    def move(self):
        head = self.body[0]
        if self.direction == "UP":
            new_head = [head[0], head[1] - block_size]
        elif self.direction == "DOWN":
            new_head = [head[0], head[1] + block_size]
        elif self.direction == "LEFT":
            new_head = [head[0] - block_size, head[1]]
        else:
            new_head = [head[0] + block_size, head[1]]
        self.body = [new_head] + self.body[:-1]

    def grow(self):
        self.body.append(self.body[-1])

class Food:
    def __init__(self):
        self.position = [random.randrange(1, width//block_size) * block_size,
                         random.randrange(1, height//block_size) * block_size]

    def respawn(self):
        self.position = [random.randrange(1, width//block_size) * block_size,
                         random.randrange(1, height//block_size) * block_size]

# Q-learning agent class
class QLearningAgent:
    def __init__(self):
        self.q_table = {}
    
    def get_state(self, snake, food):
        head = snake.body[0]
        food_dir = (food.position[0] - head[0], food.position[1] - head[1])
        body_dir = [(head[0] - part[0], head[1] - part[1]) for part in snake.body[1:]]
        return (food_dir, tuple(body_dir))

    def get_action(self, state):
        if random.uniform(0, 1) < epsilon:
            return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        return max(self.q_table.get(state, {}), key=self.q_table.get(state, {}).get, default="RIGHT")

    def update_q_value(self, state, action, reward, next_state):
        old_q_value = self.q_table.get(state, {}).get(action, 0)
        next_max = max(self.q_table.get(next_state, {}).values(), default=0)
        new_q_value = (1 - alpha) * old_q_value + alpha * (reward + gamma * next_max)
        
        if state not in self.q_table:
            self.q_table[state] = {}
        self.q_table[state][action] = new_q_value

# Game loop
def game_loop():
    global epsilon
    snake = Snake()
    food = Food()
    agent = QLearningAgent()
    clock = pygame.time.Clock()
    score = 0
    done = False

    while not done:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # Get current state
        state = agent.get_state(snake, food)

        # Choose action
        action = agent.get_action(state)
        snake.direction = action

        # Move snake
        snake.move()
        
        # Check for collision with food
        if snake.body[0] == food.position:
            snake.grow()
            food.respawn()
            reward = 10
            score += 1
        else:
            reward = -1
        
        # Check for collision with wall or itself
        head = snake.body[0]
        if (head[0] >= width or head[0] < 0 or 
            head[1] >= height or head[1] < 0 or 
            head in snake.body[1:]):
            done = True
            reward = -100

        # Update Q-values
        next_state = agent.get_state(snake, food)
        agent.update_q_value(state, action, reward, next_state)

        # Reduce epsilon (exploration rate)
        if epsilon > min_epsilon:
            epsilon *= epsilon_decay

        # Draw everything
        screen.fill(black)
        for segment in snake.body:
            pygame.draw.rect(screen, green, pygame.Rect(segment[0], segment[1], block_size, block_size))
        pygame.draw.rect(screen, red, pygame.Rect(food.position[0], food.position[1], block_size, block_size))

        # Update display and control speed
        pygame.display.flip()
        clock.tick(speed)

    return score

# Main game execution
def main():
    episodes = 1000
    scores = []

    for episode in range(episodes):
        score = game_loop()
        scores.append(score)
        print(f"Episode: {episode + 1}, Score: {score}")

    pygame.quit()

if __name__ == "__main__":
    main()