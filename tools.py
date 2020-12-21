import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import numpy
import random
import pygame


def parse_cfg(file):
    file = open(file, 'r')
    lines = [l.lstrip().rstrip() for l in file.readlines() if l != '\n']
    params = {}
    for line in lines:
        param, value = line.split('=')
        param = param.lstrip().rstrip()
        value = value.lstrip().rstrip()
        if 'color' in param:
            value = tuple(map(int, value[1:-1].replace(' ', '').split(',')))
            
        elif param == 'net_layers':
            value = list(map(int, value[1:-1].replace(' ', '').split(',')))

        elif param == 'mutation_rate' or param == 'base_percent':
            value = float(value)
        elif param in ['screen_size', 'population', 'num_generations', 'cell_size', 'is_random_seed', 'random_seed']:
            value = int(value)
        params[param] = value
    return params


params = parse_cfg('./settings.cfg')
SCREEN_SIZE = params['screen_size']
RANDOM_SEED = params['random_seed']
CELL_SIZE = params['cell_size']
if params['is_random_seed']:
    random.seed(RANDOM_SEED)
    numpy.random.seed(RANDOM_SEED)


def get_Xdata(snake, food, steps):
    Xdata = numpy.zeros((28, 1))
    parts_xs = []
    parts_ys = []
    for part in snake.parts[1:]:
        if snake.head_x == part.x and snake.head_y == part.y:
            snake.kill()
            return None
        parts_xs.append(part.x)
        parts_ys.append(part.y)
        if snake.head_x == part.x:
            if snake.head_y > part.y and Xdata[1] == 0:
                Xdata[1] = snake.head_y - part.y - 20
            elif snake.head_y < part.y and Xdata[9] == 0:
                Xdata[9] = part.y - snake.head_y - 20
        if snake.head_y == part.y:
            if snake.head_x > part.x and Xdata[13] == 0:
                Xdata[13] = snake.head_x - part.x - 20
            elif snake.head_x < part.x and Xdata[5] == 0:
                Xdata[5] = part.x - snake.head_x - 20
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
            food_x = random.choice(range(0, SCREEN_SIZE - CELL_SIZE, CELL_SIZE))
            food_y = random.choice(range(0, SCREEN_SIZE - CELL_SIZE, CELL_SIZE))
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
    Xdata[18] = SCREEN_SIZE - snake.head_x - CELL_SIZE
    Xdata[19] = ((SCREEN_SIZE-snake.head_x)**2 + (SCREEN_SIZE-snake.head_y)**2)**0.5
    Xdata[20] = SCREEN_SIZE - snake.head_y - CELL_SIZE
    Xdata[21] = ((0-snake.head_x)**2 + (SCREEN_SIZE-snake.head_y)**2)**0.5
    Xdata[22] = snake.head_x
    Xdata[23] = ((0-snake.head_x)**2 + (0-snake.head_y)**2)**0.5
    if snake.direction == 'UP':
        Xdata[24] = 1
    elif snake.direction == 'RIGHT':
        Xdata[25] = 1
    elif snake.direction == 'DOWN':
        Xdata[26] = 1
    else:
        Xdata[27] = 1
    return Xdata

def draw_grid(snake, Xdata, screen):
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, (10, 10, 10), (x, 0), (x, SCREEN_SIZE))
    for y in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, (10, 10, 10), (0, y), (SCREEN_SIZE, y))
    if Xdata[4] != 0:
        pygame.draw.line(screen, (0, 255, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (SCREEN_SIZE, snake.head_y+CELL_SIZE/2))
    else:
        pygame.draw.line(screen, (255, 0, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (SCREEN_SIZE, snake.head_y+CELL_SIZE/2))
    if Xdata[12] != 0:
        pygame.draw.line(screen, (0, 255, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (0, snake.head_y+CELL_SIZE/2))
    else:
        pygame.draw.line(screen, (255, 0, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (0, snake.head_y+CELL_SIZE/2))
    if Xdata[8] != 0:
        pygame.draw.line(screen, (0, 255, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (snake.head_x+CELL_SIZE/2, SCREEN_SIZE))
    else:
        pygame.draw.line(screen, (255, 0, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (snake.head_x+CELL_SIZE/2, SCREEN_SIZE))
    if Xdata[0] != 0:
        pygame.draw.line(screen, (0, 255, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (snake.head_x+CELL_SIZE/2, 0))
    else:
        pygame.draw.line(screen, (255, 0, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (snake.head_x+CELL_SIZE/2, 0))
    if Xdata[2] != 0:
        x = SCREEN_SIZE
        y = (snake.head_y+CELL_SIZE/2) - ((SCREEN_SIZE-(snake.head_x+CELL_SIZE/2)))
        pygame.draw.line(screen, (0, 255, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (x, y))
    else:
        x = SCREEN_SIZE
        y = (snake.head_y+CELL_SIZE/2) - ((SCREEN_SIZE-(snake.head_x+CELL_SIZE/2)))
        pygame.draw.line(screen, (255, 0, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (x, y))
    if Xdata[6] != 0:
        x = SCREEN_SIZE
        y = (snake.head_y+CELL_SIZE/2) + ((SCREEN_SIZE-(snake.head_x+CELL_SIZE/2)))
        pygame.draw.line(screen, (0, 255, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (x, y))
    else:
        x = SCREEN_SIZE
        y = (snake.head_y+CELL_SIZE/2) + ((SCREEN_SIZE-(snake.head_x+CELL_SIZE/2)))
        pygame.draw.line(screen, (255, 0, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (x, y))
    if Xdata[10] != 0:
        x = 0
        y = (snake.head_y+CELL_SIZE/2) + snake.head_x+CELL_SIZE/2
        pygame.draw.line(screen, (0, 255, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (x, y))
    else:
        x = 0
        y = (snake.head_y+CELL_SIZE/2) + snake.head_x+CELL_SIZE/2
        pygame.draw.line(screen, (255, 0, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (x, y))
    if Xdata[14] != 0:
        x = 0
        y = (snake.head_y+CELL_SIZE/2) - (snake.head_x+CELL_SIZE/2)
        pygame.draw.line(screen, (0, 255, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (x, y))
    else:
        x = 0
        y = (snake.head_y+CELL_SIZE/2) - (snake.head_x+CELL_SIZE/2)
        pygame.draw.line(screen, (255, 0, 0), (snake.head_x+CELL_SIZE/2, snake.head_y+CELL_SIZE/2), (x, y))