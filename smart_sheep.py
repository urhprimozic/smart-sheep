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
def test(generation, nets):
    text = [gui.Text("Generation " + str(generation)),
            gui.Text(str(generation_size) + " out of " + str(generation_size) + "alive")]
    delay = 50
    screen.fill(white)
    welcome = gui.Text("Testing generation " + str(generation))
    welcome.render(black, 1 / 10 * width, 2 / 3 * height, 40, screen)
    pygame.display.flip()
    pygame.time.delay(1500)
    screen.fill(background_color)
    # we are testing all the sheep in the same time
    sheep = [gui.Object(['img/sheep1.png', 'img/sheep2.png'], 100, ground_y) for i in range(generation_size)]
    # number of sheeps alive
    sheep_alive = generation_size
    # there is only 1 wolf and 1 package of food on the screen at the same time, so we dont need to create new
    wolf = gui.Object(['img/wolf1.png', 'img/wolf2.png'], width + 1, ground_y)
    food = gui.Object(['img/food1.png', 'img/food2.png', 'img/food3.png'], width + 1, ground_y)
    ground = gui.Object(['img/background.png'], 0, ground_y + 10)
    fitness = [0 for i in range(generation_size)]
    # game loop
    step = 0
    while True:
        step += 1
        # check for collisions
        for i in range(generation_size):
            if sheep[i].collision(food) and food.surface_counter == 0:
                food.animate()
                fitness[i] += food_value
            if sheep[i].collision(wolf):
                sheep_alive -= 1
                sheep[i].kill()

        pygame.time.delay(delay)

        # check for jumping
        # using NN
        # one node in first layer contains the distance to the wolf ahead ( if any), the other one to the food package
        input_layer = np.ndarray(shape=(2, 1))
        if wolf.mask.x > 100 + sheep[0].mask.height and wolf.x_bounds():
            input_layer[0][0] += 1 / (wolf.mask.x - 100 - sheep[0].mask.height)
        else:
            input_layer[0][0] = 0
        if food.mask.x > 100 + sheep[0].mask.height and food.x_bounds():
            input_layer[1][0] += 1 / (food.mask.x - 100 - sheep[0].mask.height)
        else:
            input_layer[1][0] = 0

        for i in range(generation_size):
            if not sheep[i].alive:
                continue
            output = nets[i].feedforward(input_layer)
            if output[0][0] > output[1][0]:
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
                if i.vy != 0:
                    i.vy += g
            if i.mask.y + i.mask.height > ground_y:
                i.mask.y = ground_y

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
        for i in sheep:
            i.render(screen)
        food.render(screen)
        wolf.render(screen)
        ground.render(screen)
        # text
        text[1].string = str(sheep_alive) + " out of " + str(generation_size) + " alive"
        text[0].render(black, 2 / 3 * width, 50, 20, screen)
        text[1].render(black, 2 / 3 * width, 100, 18, screen)
        pygame.display.flip()



