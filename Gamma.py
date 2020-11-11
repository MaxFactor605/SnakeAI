import sys
import pygame
import random
import time
import numpy
from pygame.locals import *


pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 40)
SNAKE_VELOCITY = 20
SCREEN_SIZE = 300
class Snake_tail():
    def __init__(self, x, y, direction, color, screen):
        self.x = x
        self.y = y
        self.screen = screen
        self.color = color
        self.direction = direction
        self.part_size = 20
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
        self.part_size = 20
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
            #sys.exit()
        elif self.x < 0:
            self.kill()
            #sys.exit()
        if self.y + 20 > SCREEN_SIZE:
            self.kill()
            #sys.exit()
        elif self.y < 0:
            self.kill()
            #sys.exit()
        
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
        self.part_size = 20
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
def get_Xdata(snake, food, steps = 0, learn = True):
    Xdata = numpy.zeros((28, 1))
    parts_xs = []
    parts_ys = []
    for part in snake.parts[1:]:
        if snake.head_x == part.x and snake.head_y == part.y:
            snake.kill()
            return None
            #sys.exit()
        parts_xs.append(part.x)
        parts_ys.append(part.y)
        if snake.head_x == part.x:
            if snake.head_y > part.y and Xdata[1] == 0:
                Xdata[1] = snake.head_y - part.y
            elif snake.head_y < part.y and Xdata[9] == 0:
                Xdata[9] = part.y - snake.head_y
        if snake.head_y == part.y:
            if snake.head_x > part.x and Xdata[13] == 0:
                Xdata[13] = snake.head_x - part.x
            elif snake.head_x < part.x and Xdata[5] == 0:
                Xdata[5] = part.x - snake.head_x
        if snake.head_x > part.x:
            if snake.head_y > part.y and Xdata[15] == 0:
                if numpy.abs(snake.head_y - part.y) == numpy.abs(snake.head_x - part.x):
                    Xdata[15] = ((part.y - snake.head_y)**2 + (part.x - snake.head_x)**2)**0.5
            elif snake.head_y < part.y and Xdata[11] == 0:
                if numpy.abs(part.y - snake.head_y) == numpy.abs(snake.head_x - part.x):
                    Xdata[11] = ((part.y - snake.head_y)**2 + (part.x - snake.head_x)**2)**0.5
        else:
            if snake.head_y > part.y and Xdata[3] == 0:
                if numpy.abs(snake.head_y - part.y) == numpy.abs(part.x - snake.head_x):
                    Xdata[3] = ((part.y - snake.head_y)**2 + (part.x - snake.head_x)**2)**0.5
            elif snake.head_y < part.y and Xdata[7] == 0:
                if numpy.abs(part.y - snake.head_y) == numpy.abs(part.x - snake.head_x):
                    Xdata[7] = ((part.y - snake.head_y)**2 + (part.x - snake.head_x)**2)**0.5
    if snake.head_x in range(food.x-5, food.x+5) and snake.head_y in range(food.y-5, food.y+5):
            snake.add_part()
            if learn:
                part = numpy.random.choice([0, 1, 2, 3])
                while True:
                    if part == food.screen_part:
                        part = numpy.random.choice([0, 1, 2, 3])
                    else:
                        break
                x, y = get_coord(part, set(parts_xs), set(parts_ys))
                food.respawn(x, y, part)
            else:
                food_x = random.choice(range(20, SCREEN_SIZE - 40, 20))
                food_y = random.choice(range(20, SCREEN_SIZE - 40, 20))
                food.respawn(food_x, food_y)
            snake.last_food = steps
    if snake.head_x == food.x:
        if snake.head_y > food.y:
            Xdata[0] = snake.head_y - food.y
            Xdata[8] = 0
        else:
            Xdata[0] = 0
            Xdata[8] = food.y - snake.head_y
    if snake.head_y == food.y:
        if snake.head_x > food.x:
            Xdata[12] = snake.head_x - food.x
            Xdata[4] = 0
        else:
            Xdata[12] = 0
            Xdata[4] = food.x - snake.head_x
    try:
        if snake.head_x > food.x:
            if snake.head_y > food.y:
                if numpy.abs(snake.head_y - food.y) == numpy.abs(food.x - snake.head_x):
                    Xdata[14] = ((food.y - snake.head_y)**2 + (food.x - snake.head_x)**2)**0.5
            else:
                if numpy.abs(food.y - snake.head_y) == numpy.abs(food.x - snake.head_x):
                    Xdata[10] = ((food.y - snake.head_y)**2 + (food.x - snake.head_x)**2)**0.5
        else:
            if snake.head_y > food.y:
                if numpy.abs(snake.head_y - food.y) == numpy.abs(snake.head_x - food.x):
                    Xdata[2] = ((food.y - snake.head_y)**2 + (food.x - snake.head_x)**2)**0.5
            else:
                if numpy.abs(food.y - snake.head_y) == numpy.abs(snake.head_x - food.x) :
                    Xdata[6] = ((food.y - snake.head_y)**2 + (food.x - snake.head_x)**2)**0.5
    except ZeroDivisionError:
        pass
    
    Xdata[16] = snake.head_y
    Xdata[17] = ((SCREEN_SIZE-snake.head_x)**2 + (0-snake.head_y)**2)**0.5
    Xdata[18] = SCREEN_SIZE - snake.head_x + 20
    Xdata[19] = ((SCREEN_SIZE-snake.head_x)**2 + (SCREEN_SIZE-snake.head_y)**2)**0.5
    Xdata[20] = SCREEN_SIZE - snake.head_y + 20
    Xdata[21] = ((0-snake.head_x)**2 + (SCREEN_SIZE-snake.head_y)**2)**0.5
    Xdata[22] = snake.head_x
    Xdata[23] = ((0-snake.head_x)**2 + (0-snake.head_y)**2)**0.5
    #Xdata = Xdata/20
    if snake.direction == 'UP':
        Xdata[24] = 1
    elif snake.direction == 'RIGHT':
        Xdata[25] = 1
    elif snake.direction == 'DOWN':
        Xdata[26] = 1
    else:
        Xdata[27] = 1
    #print(Xdata)
    #input()
    return Xdata

class Food():
    def __init__(self, x, y, color, screen, part= None):
        self.x = x
        self.y = y
        self.color = color 
        self.screen = screen
        self.surf = pygame.Surface((20, 20))
        self.surf.fill(self.color)
        self.screen.blit(self.surf, (self.x, self.y))
        self.screen_part = part

    def respawn(self, x, y, part = None):
        self.x = x
        self.y = y
        self.part = part
        self.screen.blit(self.surf, (self.x, self.y))
if __name__ == '__main__':
    screen = pygame.display.set_mode((SCREEN_SIZE,SCREEN_SIZE))
    screen.fill((32, 42, 234))
    snake = Snake(0, 0, (123, 123, 123), screen)
    
    food_x = random.choice(range(0, SCREEN_SIZE - 20, 20))
    food_y = random.choice(range(0, SCREEN_SIZE - 20, 20))
    Food = Food(food_x, food_y, (1,2,3), screen)
    pygame.display.update()
    while True:
        screen.fill((255,255,255))    
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
        print(snake.head_x, '\t', snake.head_y)
        snake.move()
        Xdata = get_Xdata(snake, Food,learn = False)
        print(Xdata)
        #input()
            
        
        Food.respawn(food_x, food_y)
        textsurf = font.render('Score: {0}'.format(snake.length), False, (0, 0, 0))
        screen.blit(textsurf, (0,0))
        for x in range(0, SCREEN_SIZE, 20):
            pygame.draw.line(screen, (10, 10, 10), (x, 0), (x, SCREEN_SIZE))
        for y in range(0, SCREEN_SIZE, 20):
            pygame.draw.line(screen, (10, 10, 10), (0, y), (SCREEN_SIZE, y))
        pygame.display.update()
        pygame.time.delay(600)

    