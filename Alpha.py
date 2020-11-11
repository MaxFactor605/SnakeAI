from Gamma import Snake, Food
import pygame
import sys
import numpy
import torch.nn.functional as F
import torch.nn as nn
import random              
import torch
import os
import time as pytime
import pygame_gui

SCREEN_SIZE = 300
SNAKE_COLOR = (255, 182, 193)
BG_COLOR = (255, 255, 255)
FOOD_COLOR = (10, 230, 78)
POPULATION = 1500
NUM_GENERATIONS = 10000
P_C = 0.1
MUTATION_RATE = 0.004
WHEEL_SELECTION = False
T = 5
class Snake_nn():
    def __init__(self, weights):
        self.input_layer_size = 28
        self.hidden_1_size = 24
        self.hidden_2_size = 18
        self.output_layer_size = 4
        if weights is None:
            self.init_weights()
        else:
            self.weights = weights
    def forward(self, X):
        '''
        Forward pass of network:
        Arguments:
            X => numpy.array of size (self.input_layer_size, 1)
        Return:
            z3 => numpy.array of size (self.output_layer_size, 1)
        '''
    
        a1 = self.weights[0]@X + self.weights[3]    
        z1 = F.leaky_relu(torch.from_numpy(a1)).numpy()
        a2 = self.weights[1]@z1 + self.weights[4]
        z2 = F.leaky_relu(torch.from_numpy(a2)).numpy()
        a3 = self.weights[2]@z2 + self.weights[5]
        z3 = torch.sigmoid(torch.from_numpy(a3)).numpy()
        return z3

    def __call__(self, X):
        return self.forward(X)


    def init_weights(self):
        '''
        Init weights for network randomly in range(-5, 5)
        '''
        self.weights1 = numpy.random.uniform(-1, 1, (self.hidden_1_size, self.input_layer_size))
        self.weights2 = numpy.random.uniform(-1, 1, (self.hidden_2_size, self.hidden_1_size))
        self.weights3 = numpy.random.uniform(-1, 1, (self.output_layer_size, self.hidden_2_size))
        self.biases1 = numpy.random.uniform(-1, 1, (self.hidden_1_size, 1))
        self.biases2 = numpy.random.uniform(-1, 1, (self.hidden_2_size, 1))
        self.biases3 = numpy.random.uniform(-1, 1, (self.output_layer_size, 1))
        self.weights = [self.weights1, self.weights2, self.weights3, self.biases1, self.biases2, self.biases3] # Weights list


def get_Xdata(snake, food, steps, learn = True):
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
                food_x = random.choice(range(0, SCREEN_SIZE - 20, 20))
                food_y = random.choice(range(0, SCREEN_SIZE - 20, 20))
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
    Xdata[18] = SCREEN_SIZE - snake.head_x - 20
    Xdata[19] = ((SCREEN_SIZE-snake.head_x)**2 + (SCREEN_SIZE-snake.head_y)**2)**0.5
    Xdata[20] = SCREEN_SIZE - snake.head_y - 20
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

def uniform_mutation(weight):
    for i in range(weight.size):
        if random.random() <= MUTATION_RATE:
            weight[i] = numpy.random.uniform(-1, 1)
    return weight

def gaussian_mutation(weight):
    for i in range(weight.size):
        if random.random() <= MUTATION_RATE:
            new_weight = random.gauss(0, 1)
            if new_weight > 1:
                new_weight = 1
            elif new_weight < -1:
                new_weight = -1
            weight[i] = new_weight
    return weight

def get_coord(part, parts_xs = set([]), parts_ys= set([])):
    if part == 0:
        try:
            x = numpy.random.choice(list(set(range(0, 101, 20)) - parts_xs))
        except ValueError:
            x = numpy.random.choice(range(0, 101, 20))
        try:
            y = numpy.random.choice(list(set(range(0, 101, 20)) - parts_ys))
        except ValueError:
            y = numpy.random.choice(range(0, 101, 20))
    elif part == 1:
        try:
            x = numpy.random.choice(list(set(range(120, 281, 20)) - parts_xs))
        except ValueError:
            x = numpy.random.choice(range(120, 281, 20))
        try:
            y = numpy.random.choice(list(set(range(0, 101, 20)) - parts_ys))
        except ValueError:
            y = numpy.random.choice(range(0, 101, 20))
    elif part == 2:
        try:
            x = numpy.random.choice(list(set(range(0, 101, 20)) - parts_xs))
        except ValueError:
            x = numpy.random.choice(range(0, 101, 20))
        try:
            y = numpy.random.choice(list(set(range(120, 281, 20)) - parts_ys))
        except ValueError:
            y = numpy.random.choice(range(120, 281, 20))
    else:
        try:
            x = numpy.random.choice(list(set(range(120, 281, 20)) - parts_xs))
        except ValueError:
            x = numpy.random.choice(range(120, 281, 20))
        try:
            y = numpy.random.choice(list(set(range(120, 281, 20)) - parts_ys))
        except ValueError:
            y = numpy.random.choice(range(120, 281, 20))

    return x, y

def uniform_crossover(nn1, nn2):
    weights1 = nn1.weights
    weights2 = nn2.weights
    weights3 = []
    weights4 = []

    for i in range(len(weights1)):
        weight1 = weights1[i]
        weight2 = weights2[i]
        shape = weight1.shape
        weight1 = weight1.reshape((weight1.size,))
        weight2 = weight2.reshape((weight2.size,))
        weight3 = numpy.zeros(weight1.shape)
        weight4 = numpy.zeros(weight2.shape)
        for gen in range(weight1.size):
            if random.random() > 0.5:
                weight3[gen] = weight1[gen]
                weight4[gen] = weight2[gen]
            else:
                weight3[gen] = weight2[gen]
                weight4[gen] = weight1[gen]

        weight3 = uniform_mutation(weight3)
        weight4 = uniform_mutation(weight4)
        weight3 = weight3.reshape(shape)
        weight4 = weight4.reshape(shape)
        weights3.append(weight3)
        weights4.append(weight4)
    return weights3, weights4


def multi_point_crossover(nn1, nn2):
    weights1 = nn1.weights
    weights2 = nn2.weights
    weights3 = []
    weights4 = []
    for i in range(len(weights1)):
        weight1 = weights1[i]
        weight2 = weights2[i]
        shape = weight1.shape
        weight1 = weight1.reshape((weight1.size,))
        weight2 = weight2.reshape((weight2.size,)) 
        weight3 = numpy.zeros(weight1.shape)
        weight4 = numpy.zeros(weight1.shape)
        #print(weight1 == weight2)
        #input()
        point_one, point_two = [random.randint(1, weight1.size//2), random.randint(weight1.size//2, weight1.size)]
        
        weight3[:point_one] = weight1[:point_one]
        weight3[point_one:point_two] = weight2[point_one:point_two]
        weight3[point_two:] = weight1[point_two:]
        weight4[:point_one] = weight2[:point_one]
        weight4[point_one:point_two] = weight1[point_one:point_two]
        weight4[point_two:] = weight2[point_two:]
            
        weight3 = uniform_mutation(weight3)
        weight4 = uniform_mutation(weight4)
        weight3 = weight3.reshape(shape)
        weight4 = weight4.reshape(shape)
        #print(weight4.shape, '\t', weight3.shape, '\t', weight1.shape)
        weights3.append(weight3)
        weights4.append(weight4)
    return (weights3, weights4)

def fitness_function(time, score):
    return time + (2*score + (score**2.1)*500) - ((score**1.2)*((0.25*time)**1.3))

if __name__ == '__main__':
    child_nns = {}
    for i in range(POPULATION):
        if os.path.exists('./Weights/Snake{0}.weights.npy'.format(i)):
            weights = numpy.load('./Weights/Snake{0}.weights.npy'.format(i), allow_pickle=True)
            child_nns[i] = Snake_nn(weights)
    speed = 0
    for generation in range(NUM_GENERATIONS):
        start_time = pytime.time()
        screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE+30))
        screen.fill(BG_COLOR)
        manager = pygame_gui.UIManager((300, 330))
        rect = pygame.Rect((0, 310), (300, 315))
        slider = pygame_gui.elements.ui_horizontal_slider.UIHorizontalSlider(rect, speed, [0, 100], manager)
        clock = pygame.time.Clock()
        population_list = {}
        for i in range(POPULATION):
            snake = Snake(120, 120, SNAKE_COLOR, screen)
            part = numpy.random.choice([0,1,2,3])
            food_x, food_y = get_coord(part)
            food = Food(food_x, food_y, FOOD_COLOR, screen, part)
            population_list[i] = [snake, food]

        pygame.init()
        pygame.font.init()
        font = pygame.font.SysFont('Comic Sans MS', 20)
        if not child_nns:
            nn_list = {}
            for i in range(POPULATION):
                nn_list[i] = Snake_nn(None)
        else:
            nn_list = child_nns
       
        scores = {}
        for i in nn_list.keys():
            snake, food = population_list[i]
            steps = 0
            while True:
                time_delta = 0

                screen.fill((255,255,255))
                
                manager.update(time_delta)
                slider.update(time_delta)
                manager.draw_ui(screen)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    manager.process_events(event)

                snake.move()
                Xdata = get_Xdata(snake, food, steps, False)
                if Xdata is None:
                    snake.kill()
                if not snake.is_alive:
                    population_list.pop(i, None)
                    scores[i] = [snake.length-2, steps]
                    break
                Ydata = nn_list[i](Xdata)
                
                out = numpy.where(Ydata == numpy.max(Ydata))[0][0]
                
                if out == 0 and snake.direction != 'DOWN':
                    snake.turn('UP')
                elif out == 1 and snake.direction != 'LEFT':
                    snake.turn('RIGHT')
                elif out == 2 and snake.direction != 'UP':
                    snake.turn('DOWN')
                elif out ==  3 and snake.direction != 'RIGHT':
                    snake.turn('LEFT')
              
                food.respawn(food.x, food.y, food.screen_part)
                if (steps - snake.last_food) >= 100:
                    snake.kill()
       
                steps += 1
                textsurf = font.render('Generation: {0}'.format(generation, i), False, (0, 0, 0))
                textsurf2 = font.render('Snake: {0}'.format(i), False, (0, 0, 0))
                textsurf3 = font.render('Score: {0}'.format(snake.length-2), False, (0, 0, 0))
                #textsurf4 = font.render('Steps: {0}'.format(steps), False, (0, 0, 0))
                screen.blit(textsurf, (0,0))
                screen.blit(textsurf2, (0,10))
                screen.blit(textsurf3, (0,20))
                #screen.blit(textsurf4, (0,30))
                for x in range(0, SCREEN_SIZE, 20):
                    pygame.draw.line(screen, (10, 10, 10), (x, 0), (x, SCREEN_SIZE))
                for y in range(0, SCREEN_SIZE, 20):
                    pygame.draw.line(screen, (10, 10, 10), (0, y), (SCREEN_SIZE, y))
                if Xdata[4] != 0:
                    pygame.draw.line(screen, (0, 255, 0), (snake.head_x+10, snake.head_y+10), (SCREEN_SIZE, snake.head_y+10))
                else:
                    pygame.draw.line(screen, (255, 0, 0), (snake.head_x+10, snake.head_y+10), (SCREEN_SIZE, snake.head_y+10))
                if Xdata[12] != 0:
                    pygame.draw.line(screen, (0, 255, 0), (snake.head_x+10, snake.head_y+10), (0, snake.head_y+10))
                else:
                    pygame.draw.line(screen, (255, 0, 0), (snake.head_x+10, snake.head_y+10), (0, snake.head_y+10))
                if Xdata[8] != 0:
                    pygame.draw.line(screen, (0, 255, 0), (snake.head_x+10, snake.head_y+10), (snake.head_x+10, SCREEN_SIZE))
                else:
                    pygame.draw.line(screen, (255, 0, 0), (snake.head_x+10, snake.head_y+10), (snake.head_x+10, SCREEN_SIZE))
                if Xdata[0] != 0:
                    pygame.draw.line(screen, (0, 255, 0), (snake.head_x+10, snake.head_y+10), (snake.head_x+10, 0))
                else:
                    pygame.draw.line(screen, (255, 0, 0), (snake.head_x+10, snake.head_y+10), (snake.head_x+10, 0))
                if Xdata[2] != 0:
                    x = SCREEN_SIZE
                    y = (snake.head_y+10) - ((SCREEN_SIZE-(snake.head_x+10)))
                    pygame.draw.line(screen, (0, 255, 0), (snake.head_x+10, snake.head_y+10), (x, y))
                else:
                    x = SCREEN_SIZE
                    y = (snake.head_y+10) - ((SCREEN_SIZE-(snake.head_x+10)))
                    pygame.draw.line(screen, (255, 0, 0), (snake.head_x+10, snake.head_y+10), (x, y))
                if Xdata[6] != 0:
                    x = SCREEN_SIZE
                    y = (snake.head_y+10) + ((SCREEN_SIZE-(snake.head_x+10)))
                    pygame.draw.line(screen, (0, 255, 0), (snake.head_x+10, snake.head_y+10), (x, y))
                else:
                    x = SCREEN_SIZE
                    y = (snake.head_y+10) + ((SCREEN_SIZE-(snake.head_x+10)))
                    pygame.draw.line(screen, (255, 0, 0), (snake.head_x+10, snake.head_y+10), (x, y))
                if Xdata[10] != 0:
                    x = 0
                    y = (snake.head_y+10) + snake.head_x+10
                    pygame.draw.line(screen, (0, 255, 0), (snake.head_x+10, snake.head_y+10), (x, y))
                else:
                    x = 0
                    y = (snake.head_y+10) + snake.head_x+10
                    pygame.draw.line(screen, (255, 0, 0), (snake.head_x+10, snake.head_y+10), (x, y))
                if Xdata[14] != 0:
                    x = 0
                    y = (snake.head_y+10) - (snake.head_x+10)
                    pygame.draw.line(screen, (0, 255, 0), (snake.head_x+10, snake.head_y+10), (x, y))
                else:
                    x = 0
                    y = (snake.head_y+10) - (snake.head_x+10)
                    pygame.draw.line(screen, (255, 0, 0), (snake.head_x+10, snake.head_y+10), (x, y))
                pygame.display.update()
                speed = slider.get_current_value()
                #print(Xdata)
                #input()
                pygame.time.delay(speed)
   
        fitnesses = {}
        sum_fitnesses = 0
        max_fitness = 0
        best_snake = []
        for i, score in scores.items():
            score_number, time = score
            fitness = fitness_function(time, score_number)
            print('Snake number: {0}\tTime: {1}\tScore: {2}\tFitness: {3}'.format(i, time, score_number, fitness))
            sum_fitnesses += fitness
            fitnesses[i] = fitness
            if fitness > max_fitness:
                max_fitness = fitness
                best_snake = [i, score_number, time]
    
        probabilties = numpy.zeros((POPULATION,))
        fitnesses = {k:v for k,v in sorted(fitnesses.items() , key = lambda item: item[1])}
        if WHEEL_SELECTION:
            for i, (num, fit) in enumerate(list(fitnesses.items())[::-1]):
                probabilties[num] = fit/sum_fitnesses
        else:
            for i, (num, fit) in enumerate(list(fitnesses.items())[::-1]):
                probabilties[num] = ((1 - P_C)**i)*P_C
        #print('probabilites')
        #print(probabilties)
        #input()
        print('Sum Fitnesses: {0} \t Average Fitness: {1} \t Max Fitness: {2}'.format(sum_fitnesses, sum_fitnesses/POPULATION, max(fitnesses.values())))
        print('Best Snake:\n\tNumber: {0}\t score: {1}\t time:{2}'.format(best_snake[0], best_snake[1], best_snake[2]))
        child_nns = {}
        num = 0 
        while len(child_nns) < POPULATION:
            parent1 = numpy.random.choice(numpy.array(sorted(scores)), 1, p=probabilties)
            while True:
                parent2 = numpy.random.choice(numpy.array(sorted(scores)), 1, p=probabilties)
                if parent1 != parent2:
                    break
           
            childrens = multi_point_crossover(nn_list[int(parent1)], nn_list[int(parent2)])
       
            child_nns[num] = Snake_nn(childrens[0])
            child_nns[num+1] = Snake_nn(childrens[1])
        
            num += 2

        if (generation+1)%10 == 0:
            for i in range(POPULATION):
                if os.path.exists('./Weights/Snake{0}.weights.npy'.format(i)):
                    os.remove('./Weights/Snake{0}.weights.npy'.format(i))


            for id, nn in child_nns.items():
                weights = nn.weights
                numpy_weights = numpy.array(weights)
                numpy.save('./Weights/Snake{0}.weights'.format(id), numpy_weights)
            print('Saved')





