from game import Snake, Food
from tools import get_Xdata, parse_cfg, draw_grid
from net import Snake_nn
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys
import numpy
import random              
import time as pytime
import pygame_gui


params = parse_cfg('./settings.cfg')
SCREEN_SIZE = params['screen_size']
SNAKE_COLOR = params['snake_color']
BG_COLOR = params['bg_color']
FOOD_COLOR = params['food_color']
POPULATION = params['population']
NUM_GENERATIONS = params['num_generations']
MUTATION_RATE = params['mutation_rate']
P_C = params['base_percent']
NET_LAYERS = params['net_layers']
WEIGHTS_FOLDER = params['weights_folder']
RANDOM_SEED = params['random_seed']
if params['selection_type'] == 'wheel':
    WHEEL_SELECTION = True
else:
    WHEEL_SELECTION = False
if params['crossover_type'] == 'uniform':
    UNIFOM_CROSSOVER = True
else:
    UNIFOM_CROSSOVER = False
if params['mutation_type'] == 'gauss':
    GAUSS_MUTATION = True
else:
    GAUSS_MUTATION = False
if params['is_random_seed']:
    random.seed(RANDOM_SEED)
    numpy.random.seed(RANDOM_SEED)

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
        if GAUSS_MUTATION:
            weight3 = gaussian_mutation(weight3)
            weight4 = gaussian_mutation(weight4)
        else:
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
        point_one, point_two = [random.randint(1, weight1.size//2), random.randint(weight1.size//2, weight1.size)]
        
        weight3[:point_one] = weight1[:point_one]
        weight3[point_one:point_two] = weight2[point_one:point_two]
        weight3[point_two:] = weight1[point_two:]
        weight4[:point_one] = weight2[:point_one]
        weight4[point_one:point_two] = weight1[point_one:point_two]
        weight4[point_two:] = weight2[point_two:]
            
        if GAUSS_MUTATION:
            weight3 = gaussian_mutation(weight3)
            weight4 = gaussian_mutation(weight4)
        else:
            weight3 = uniform_mutation(weight3)
            weight4 = uniform_mutation(weight4)
        weight3 = weight3.reshape(shape)
        weight4 = weight4.reshape(shape)
        weights3.append(weight3)
        weights4.append(weight4)
    return (weights3, weights4)


def fitness_function(time, score):
    return time + (2*score + (score**2.1)*500) - ((score**1.2)*((0.25*time)**1.3))



if __name__ == '__main__':
    child_nns = {}
    if not os.path.exists('./{0}'.format(WEIGHTS_FOLDER)):
        os.mkdir('./{0}'.format(WEIGHTS_FOLDER))
    for i in range(POPULATION):
        if os.path.exists('./{1}/Snake{0}.weights.npy'.format(i, WEIGHTS_FOLDER)):
            weights = numpy.load('./{1}/Snake{0}.weights.npy'.format(i, WEIGHTS_FOLDER), allow_pickle=True)
            child_nns[i] = Snake_nn(NET_LAYERS, weights)
    speed = 0
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Comic Sans MS', 20)
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
            food_x = random.choice(range(0, SCREEN_SIZE - 20, 20))
            food_y = random.choice(range(0, SCREEN_SIZE - 20, 20))
            food = Food(food_x, food_y, FOOD_COLOR, screen)
            population_list[i] = [snake, food]

        
        if not child_nns:
            nn_list = {}
            for i in range(POPULATION):
                nn_list[i] = Snake_nn(NET_LAYERS, None)
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
                Xdata = get_Xdata(snake, food, steps)
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
              
                food.respawn(food.x, food.y)
                if (steps - snake.last_food) >= 100:
                    snake.kill()
       
                steps += 1
                textsurf = font.render('Generation: {0}'.format(generation, i), False, (0, 0, 0))
                textsurf2 = font.render('Snake: {0}'.format(i), False, (0, 0, 0))
                textsurf3 = font.render('Score: {0}'.format(snake.length-2), False, (0, 0, 0))
                screen.blit(textsurf, (0,0))
                screen.blit(textsurf2, (0,10))
                screen.blit(textsurf3, (0,20))

                draw_grid(snake, Xdata, screen)
                pygame.display.update()
                speed = slider.get_current_value()
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
            if UNIFOM_CROSSOVER:
                childrens = uniform_crossover(nn_list[int(parent1)], nn_list[int(parent2)])
            else:
                childrens = multi_point_crossover(nn_list[int(parent1)], nn_list[int(parent2)])
       
            child_nns[num] = Snake_nn(NET_LAYERS, childrens[0])
            child_nns[num+1] = Snake_nn(NET_LAYERS, childrens[1])
        
            num += 2

        if (generation+1)%10 == 0:
            for i in range(POPULATION):
                if os.path.exists('./{1}/Snake{0}.weights.npy'.format(i, WEIGHTS_FOLDER)):
                    os.remove('./{1}/Snake{0}.weights.npy'.format(i, WEIGHTS_FOLDER))


            for id, nn in child_nns.items():
                weights = nn.weights
                numpy_weights = numpy.array(weights)
                numpy.save('./{1}/Snake{0}.weights'.format(id, WEIGHTS_FOLDER), numpy_weights)
            print('Saved')





