import pygame
import random
import pygame.freetype
import os
import net
import numpy as np
import time
import pygame.locals
import gui
from settings import *
import math

# preperation
dir_name = os.path.dirname(__file__)
pygame.init()
pygame.freetype.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((width, height))  # + log_width
pygame.display.set_caption('Smart Sheep')


def events():
    # -1 for destroying the generation, 1,2,3 for speeds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            q = input("Exit?[y/n]")
            if q == "y" or q == "Y":
                os._exit(1)
            else:
                a = input("tvoj starš 2 je homoseksualec")
                if a == "english":
                    print("ur mom gay lol learn slovene")
        # --------------add code----------------
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return -1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            return 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            return 2
        if event.type == pygame.KEYDOWN and event.key == pygame.K_3:
            return 3
        if event.type == pygame.KEYDOWN and event.key == pygame.K_4:
            return 4
        if event.type == pygame.KEYDOWN and event.key == pygame.K_5:
            return 5


# test a generation. nets should be an array of net.Median or net.Cross_over.
# returns an array of fitneses for every sheep
def test(generation, generation_size, nets):
    text = [gui.Text("Generation " + str(generation)),
            gui.Text(str(generation_size) + " out of " + str(generation_size) + "alive")]
    delay = 0
    screen.fill(white)
    welcome = gui.Text("Testing generation " + str(generation))
    welcome.render(black, 1 / 10 * width, 2 / 3 * height, 40, screen)
    pygame.display.flip()
    pygame.time.delay(500)
    screen.fill(background_color)
    # we are testing all the sheep in the same time
    sheep = [gui.Object(['img/sheep1.png', 'img/sheep2.png'], 100, ground_y) for i in range(generation_size)]
    # number of sheeps alive
    sheep_alive = generation_size
    # there is only 1 wolf and 1 package of food on the screen at the same time, so we dont need to create new
    wolf = gui.Object(['img/wolf1.png', 'img/wolf2.png'], width + 1, ground_y)
    food = gui.Object(['img/food1.png', 'img/food2.png', 'img/food3.png'], width + 1, ground_y)
    ground = gui.Object(['img/background.png'], 0, ground_y + 10)
    fitness = [1 for i in range(generation_size)]
    # game loop
    step = 0
    while True:
        step += 1
        # check for collisions
        for i in range(generation_size):
            if not sheep[i].alive:
                continue
            if sheep[i].collision(food) and food.surface_counter == 0:
                food.animate()
                fitness[i] += food_value
                sheep[i].hunger = 0
            if sheep[i].collision(wolf) and wolf.x_bounds():
                sheep_alive -= 1
                sheep[i].kill()
        if wolf.x_bounds() and wolf.mask.right < 100:
            for i in range(generation_size):
                if sheep[i].alive:
                    fitness[i] += wolf_value

        pygame.time.delay(delay)

        # check for jumping
        # using NN
        # one node in first layer contains the distance to the wolf ahead ( if any), the other one to the food package
        input_layer = np.ndarray(shape=(2, 1))
        if wolf.mask.x > 100 + sheep[0].mask.height and wolf.x_bounds():
            input_layer[0][0] += 1 / math.sqrt(wolf.mask.x - 100 - sheep[0].mask.height)
        else:
            input_layer[0][0] = 0

        if food.mask.x > 100 + sheep[0].mask.height and food.x_bounds():
            input_layer[1][0] += 1 / math.sqrt(food.mask.x - 100 - sheep[0].mask.height)
        else:
            input_layer[1][0] = 0

        for i in range(generation_size):
            if not sheep[i].alive:
                continue
                # increase fitness !!
            fitness[i] += step_value
            output = nets[i].feed_forward(input_layer)
            if output[0][0] > output[1][0] and sheep[i].vy == 0 and sheep[i].mask.bottom == ground_y:
                sheep[i].vy = sheep_jump
        # move
        if not wolf.x_bounds():
            if random.randint(1, wolf_spawn_chance) == 2:
                wolf.move_to_x(width - 1)
        if not food.x_bounds():
            if random.randint(1, food_spawn_chance) == 2:
                food.surface_counter = 0
                food.move_to_x(width - 1)

        ground.move_by(food_speed, 0)
        if ground.mask.x < -800:
            ground.move_to(0, ground.mask.y)
        if food.x_bounds():
            food.move_by(food_speed, 0)
        if wolf.x_bounds():
            wolf.move_by(wolf_speed, 0)
        for i in sheep:
            if i.alive:
                i.move_by(0, i.vy)
                if i.mask.bottom < ground_y:
                    i.vy += g
            if i.mask.bottom > ground_y or (i.vy >= 0 and i.mask.bottom == ground_y):
                i.mask.y = ground_y - i.mask.height
                i.vy = 0

        #hunger
        for i in sheep:
            i.hunger += hunger_value
            if i.hunger > max_hunger:
                i.kill()

        # events
        speed = events()
        if speed == -1:
            return fitness
        if speed == 1:
            delay = 0
        if speed == 2:
            delay = 30
        if speed == 3:
            delay = 500
        if speed == 4:
            delay -= 10
        if speed == 5:
            delay += 10

        # animations
        if food.mask.right < 100 and food.surface_counter == 1:
            food.animate()
        if step % anime_speed == 0:
            wolf.animate()
            for i in sheep:
                i.animate()

        # rendering
        screen.fill(background_color)
        food.render(screen)
        for i in sheep:
            i.render(screen)
        wolf.render(screen)
        ground.render(screen)
        # text
        text[1].string = str(sheep_alive) + " out of " + str(generation_size) + " alive"
        text[0].render(black, 2 / 3 * width, 50, 20, screen)
        text[1].render(black, 2 / 3 * width, 100, 18, screen)
        pygame.display.flip()

        if sheep_alive <= 0:
            return fitness


# using array fitness (with elements = ftneses of all the sheep) returns an index
def select_parent(fitness):
    choice = random.randint(0, int(sum(fitness)))
    sumus = 0
    for i in range(len(fitness)):
        sumus += fitness[i]
        if choice <= sumus:
            return i


def ga(generation_size, max_generation):
    print("Genetic algorithm. Generation size ", generation_size, "Max generation ", max_generation)
    generation = 0
    # contains max fitness
    max_fitness = 0
    # contains all the fintess
    fitness_all = []
    # contains max fitnes from a generation
    fitness_max = []
    parents = [net.Cross_over(net_size) for i in range(generation_size)]
    fitness = [1 for i in range(generation_size)]
    while generation <= max_generation:
        print("Testing generation ", generation)
        generation += 1
        # shuffle
        if max_fitness == 0:
            parents = [net.Cross_over(net_size) for i in range(generation_size)]
        children = [net.Cross_over(net_size, parents[select_parent(fitness)], parents[select_parent(fitness)]) for i in
                    range(generation_size)]
        fitness = test(generation, generation_size, children)
        fitness_max.append(max(fitness))
        max_fitness = max(max_fitness, fitness_max[-1])
        print("   best fitness in ", generation, ": ", fitness_max[-1])
        fitness_all.append(fitness)
        parents = children[:]

    dict_fitness = {"best fitness": max_fitness, "best fitness growth": fitness_max, "all results": fitness_all,
                    "last generation": children}
    return dict_fitness


ga(800, 3000)
