import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import sys
import pygame
import random
import time
import numpy
from pygame.locals import *
from tools import parse_cfg


params = parse_cfg('./settings.cfg')
SNAKE_VELOCITY = params['cell_size']
SCREEN_SIZE = params['screen_size']
CELL_SIZE = params['cell_size']
BG_COLOR = params['bg_color']
FOOD_COLOR = params['food_color']
SNAKE_COLOR = params['snake_color']

class Snake_tail():
    def __init__(self, x, y, direction, color, screen):
        self.x = x
        self.y = y
        self.screen = screen
        self.color = color
        self.direction = direction
        self.part_size = CELL_SIZE
        self.surf = pygame.Surface((self.part_size, self.part_size))
        self.surf.fill(self.color)
        self.turn_dots = []
        self.screen.blit(self.surf, (self.x, self.y))
        
    def move(self):
        if self.turn_dots:
            dot = self.turn_dots[0]
            if self.x == dot['x'] and self.y == dot['y']:
                self.turn(dot['direction'])
                self.turn_dots = self.turn_dots[1:]
        if self.direction == 'DOWN':
            self.y += SNAKE_VELOCITY
        elif self.direction == 'UP':
            self.y -= SNAKE_VELOCITY
        elif self.direction == 'LEFT':
            self.x -= SNAKE_VELOCITY
        elif self.direction == 'RIGHT':
            self.x += SNAKE_VELOCITY
        self.screen.blit(self.surf, (self.x, self.y))

    def turn(self, direction):
        self.direction = direction

    def add_turn_dot(self, x, y, direction):
        dot = {'x':x, 'y':y, 'direction':direction}
        self.turn_dots.append(dot)
    
    
class Snake_head():
    def __init__(self, x, y, color, screen):
        self.x = x
        self.y = y
        self.screen = screen
        self.direction = 'DOWN'
        self.part_size = CELL_SIZE
        self.color = color
        self.surf = pygame.Surface((self.part_size, self.part_size))
        self.surf.fill(self.color)
        self.screen.blit(self.surf, (self.x, self.y))
        self.is_alive = True

    def move(self):
        if self.direction == 'DOWN':
            self.y += SNAKE_VELOCITY
        elif self.direction == 'UP':
            self.y -= SNAKE_VELOCITY
        elif self.direction == 'LEFT':
            self.x -= SNAKE_VELOCITY
        elif self.direction == 'RIGHT':
            self.x += SNAKE_VELOCITY
        if self.x + 20 > SCREEN_SIZE:
            self.kill()
        elif self.x < 0:
            self.kill()
        if self.y + 20 > SCREEN_SIZE:
            self.kill()
        elif self.y < 0:
            self.kill()
           
        
        self.screen.blit(self.surf, (self.x, self.y))
    def turn(self, direction):
        self.direction = direction

    def kill(self):
        self.is_alive = False


class Snake():
    def __init__(self, x, y, color, screen):
        self.head_x = x
        self.head_y = y
        self.length = 2
        self.screen = screen
        self.color = color
        self.direction = 'DOWN'
        self.parts = [Snake_head(self.head_x, self.head_y, self.color, self.screen)]
        self.part_size = CELL_SIZE
        self.living_time = time.time()
        for i in range(1,self.length):
            self.parts.append(Snake_tail(self.head_x, self.head_y-(self.part_size)*i, self.direction, self.color, self.screen))
        self.is_alive = True
        self.last_food = 0

    def move(self):
        for part in self.parts:
            part.move()
        head = self.parts[0]
        if head.is_alive:
            self.head_x = head.x
            self.head_y = head.y
        else:
            self.kill()
        
    def turn(self, direction):
        head = self.parts[0]
        head.turn(direction)
        self.direction = direction
        for part in self.parts[1:]:
            part.add_turn_dot(head.x, head.y, direction)

    def add_part(self):
        last_part = self.parts[-1]
        if last_part.direction == 'DOWN':
            part = Snake_tail(last_part.x, last_part.y-self.part_size, 'DOWN', self.color, self.screen)
        elif last_part.direction == 'UP':
            part = Snake_tail(last_part.x, last_part.y+self.part_size, 'UP', self.color, self.screen)
        elif last_part.direction == 'LEFT':
            part = Snake_tail(last_part.x+self.part_size, last_part.y, 'LEFT', self.color, self.screen)
        elif last_part.direction == 'RIGHT':
            part = Snake_tail(last_part.x-self.part_size, last_part.y, 'RIGHT', self.color, self.screen)
        for dot in last_part.turn_dots:
            part.add_turn_dot(**dot)
        self.parts.append(part)
        self.length += 1

    def kill(self):
        self.is_alive = False
        self.living_time = time.time() - self.living_time


class Food():
    def __init__(self, x, y, color, screen):
        self.x = x
        self.y = y
        self.color = color 
        self.screen = screen
        self.surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.surf.fill(self.color)
        self.screen.blit(self.surf, (self.x, self.y))

    def respawn(self, x, y):
        self.x = x
        self.y = y
        self.screen.blit(self.surf, (self.x, self.y))

if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Comic Sans MS', 40)
    screen = pygame.display.set_mode((SCREEN_SIZE,SCREEN_SIZE))
    screen.fill(BG_COLOR)
    snake = Snake(0, 0, SNAKE_COLOR, screen)
    
    food_x = random.choice(range(0, SCREEN_SIZE - 20, 20))
    food_y = random.choice(range(0, SCREEN_SIZE - 20, 20))
    Food = Food(food_x, food_y, FOOD_COLOR, screen)
    pygame.display.update()
    while True:
        screen.fill(BG_COLOR)    
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_DOWN and snake.direction != 'UP':
                    snake.turn('DOWN')
                elif event.key == K_UP and snake.direction != 'DOWN':
                    snake.turn('UP')
                elif event.key == K_LEFT and snake.direction != 'RIGHT':
                    snake.turn('LEFT')
                elif event.key == K_RIGHT and snake.direction != 'LEFT':
                    snake.turn('RIGHT')
                elif event.key == K_SPACE:
                    snake.add_part()
                elif event.key == pygame.K_ESCAPE:
                    input()

        if snake.head_x in range(food_x-15, food_x+15) and snake.head_y in range(food_y-15, food_y+15):
            snake.add_part()
            food_x = random.choice(range(0, SCREEN_SIZE - 20, 20))
            food_y = random.choice(range(0, SCREEN_SIZE - 20, 20))
        for part in snake.parts[1:]:
            if snake.head_x in range(part.x-6, part.x+6) and snake.head_y in range(part.y-6, part.y+6):
                print('END GAME')
                sys.exit()

        snake.move()
        
            
        
        Food.respawn(food_x, food_y)
        textsurf = font.render('Score: {0}'.format(snake.length), False, (0, 0, 0))
        screen.blit(textsurf, (0,0))
        for x in range(0, SCREEN_SIZE, 20):
            pygame.draw.line(screen, (10, 10, 10), (x, 0), (x, SCREEN_SIZE))
        for y in range(0, SCREEN_SIZE, 20):
            pygame.draw.line(screen, (10, 10, 10), (0, y), (SCREEN_SIZE, y))
        pygame.display.update()
        pygame.time.delay(60)

    