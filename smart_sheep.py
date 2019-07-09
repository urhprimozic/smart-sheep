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
pygame.mixer.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((width, height))  # + log_width
pygame.display.set_caption('Smart Sheep')

americano_active = False

buttons = [gui.Text("START"), gui.Text("Start manual"), gui.Text("Settings"),
           gui.Text("Stop music")]

my_hot_mixtape = os.path.join(dir_name, 'sound/sheep-theme.mp3')
pygame.mixer.music.load(my_hot_mixtape)
pygame.mixer.music.play(-1)

def render_buttons():
    buttons[0].render(black, 10, 420, 22, screen)
    buttons[1].render(black, 210, 420, 22, screen)
    buttons[2].render(black, 410, 420, 22, screen)
    buttons[3].render(black, 610, 420, 22, screen)


def events():
    # -1 for destroying the generation, 1,2,3 for speeds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            # q = input("Exit?[y/n]")
            # if q == "y" or q == "Y":
            os._exit(1)
            # else:
            #   a = input("tvoj starš 2 je homoseksualec")
            # if a == "english":
            #   print("ur mom gay lol learn slovene")
            return -2
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
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if gui.in_bounds(pos[0], pos[1], 10, 420, 200, 60):
                return 10
            if gui.in_bounds(pos[0], pos[1], 210, 420, 200, 60):
                return 11
            if gui.in_bounds(pos[0], pos[1], 410, 420, 200, 60):
                return 12
            if gui.in_bounds(pos[0], pos[1], 610, 420, 200, 60):
                return 13


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

        # hunger
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

        if speed == 10:
            buttons[0].string = "START"
            fitness = []
            return fitness

        if speed == 13:
            if buttons[3].string == "Stop music":
                pygame.mixer.music.pause()
                buttons[3].string = "Start music"
            else:
                pygame.mixer.music.unpause()
                buttons[3].string = "Stop music"

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
        render_buttons()
        pygame.display.flip()

        if sheep_alive <= 0:
            return fitness


def manual():
    global screen
    if not americano_active:
        screen = pygame.display.set_mode((width, height))
    sheep = gui.Object(['img/sheep1.png', 'img/sheep2.png'], 100, ground_y)
    wolf = gui.Object(['img/wolf1.png', 'img/wolf2.png'], width + 1, ground_y)
    food = gui.Object(['img/food1.png', 'img/food2.png', 'img/food3.png'], width + 1, ground_y)
    ground = gui.Object(['img/background.png'], 0, ground_y + 10)
    hunger_text = gui.Text("0")
    score_text = gui.Text("0")
    step = 0
    while True:
        step += 1
        # collisions
        if sheep.collision(wolf):
            text = gui.Text("Game Over")
            text.render(black, 1 / 3 * width, 50, 22, screen)
            pygame.display.flip()
            pygame.time.delay(2000)
            # don't overuse it ;)
            manual()
            return -1
            buttons[1].string = "Start manual"
        if sheep.collision(food):
            if food.surface_counter == 0:
                sheep.hunger = 0
                food.animate()

        # increase the hunger
        sheep.hunger += 1

        # check for max hunger
        if sheep.hunger > 600:
            text = gui.Text("Game Over")
            text.render(black, 1 / 3 * width, 50, 22, screen)
            pygame.display.flip()
            pygame.time.delay(2000)
            # don't overuse it ;)
            manual()
            return -1
            buttons[1].string = "Start manual"

        # input
        event = events()
        if event == 11:
            buttons[1].string = "Start manual"
            return -1
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if sheep.mask.bottom == ground_y:
                sheep.vy = -18
        if event == 13:
            if buttons[3].string == "Stop music":
                pygame.mixer.music.pause()
                buttons[3].string = "Start music"
            else:
                pygame.mixer.music.unpause()
                buttons[3].string = "Stop music"

        # movement
        if not wolf.x_bounds():
            if random.randint(1, wolf_spawn_chance) == 2:
                wolf.move_to_x(width - 1)
        if not food.x_bounds():
            if random.randint(1, food_spawn_chance) == 2:
                food.surface_counter = 0
                food.move_to_x(width - 1)

        if ground.mask.x < -800:
            ground.move_to(0, ground.mask.y)

        wolf.move_by(wolf_speed, 0)
        food.move_by(food_speed, 0)
        ground.move_by(food_speed, 0)

        sheep.move_by(0, sheep.vy)
        sheep.vy += g
        # if sheep is too low
        if sheep.mask.bottom > ground_y:
            sheep.vy = 0
            sheep.mask.y = ground_y - sheep.mask.height

        # rendering
        if food.mask.right < sheep.mask.x and food.surface_counter == 1:
            food.animate()

        if step % anime_speed == 0:
            wolf.animate()
            sheep.animate()

        score_text.string = "score: " + str(step)
        hunger_text.string = "hunger: " + str(sheep.hunger)
        screen.fill(background_color)
        score_text.render(black, 650, 5, 18, screen)
        if sheep.hunger > 500:
            hunger_text.render((255, 10, 10), 650, 30, 18, screen)
        else:
            hunger_text.render(black, 650, 30, 18, screen)
        wolf.render(screen)
        food.render(screen)
        sheep.render(screen)
        ground.render(screen)
        pygame.time.delay(17)
        render_buttons()
        pygame.display.flip()


# using array fitness (with elements = ftneses of all the sheep) returns an index
def select_parent(fitness):
    choice = random.randint(0, int(sum(fitness)))
    sumus = 0
    for i in range(len(fitness)):
        sumus += fitness[i]
        if choice <= sumus:
            return i


def ga(generation_size, max_generation):
    global screen
    if not americano_active:
        screen = pygame.display.set_mode((width, height))
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
    while generation <= max_generation or max_generation == -3:
        print("Testing generation ", generation)
        generation += 1
        # shuffle
        if max_fitness == 0:
            parents = [net.Cross_over(net_size) for i in range(generation_size)]
        children = [net.Cross_over(net_size, parents[select_parent(fitness)], parents[select_parent(fitness)]) for i in
                    range(generation_size)]
        fitness = test(generation, generation_size, children)
        if len(fitness) == 0:
            return -3
        fitness_max.append(max(fitness))
        max_fitness = max(max_fitness, fitness_max[-1])
        print("   best fitness in ", generation, ": ", fitness_max[-1])
        fitness_all.append(fitness)
        parents = children[:]

    dict_fitness = {"best fitness": max_fitness, "best fitness growth": fitness_max, "all results": fitness_all,
                    "last generation": children}
    return dict_fitness


def americano(has_oil=False):
    global screen, americano_active
    americano_active = True
    if has_oil:
        genocide = country_of_peace()
        genocide.invade_with_guns()

    screen = pygame.display.set_mode((width, height + 100))
    generation_size_default = 800
    while events() != -2:
        screen.fill(white)
        render_buttons()
        pygame.display.flip()
        event = events()
        if event == 10:
            buttons[0].string = "Stop"
            ga(generation_size_default, -3)
        if event == 11:
            buttons[1].string = "Stop Manual"
            manual()
        if event == 12:
            buttons[2].string = "Enter values in terminal"
            screen.fill(white)
            buttons[2].render(black, 410, 420, 13, screen)
            pygame.display.flip()
            global food_spawn_chance, wolf_spawn_chance, mutation_props, net_size
            print("Enter new values here. Default values are in ().")
            print("ctrl+C to guit")
            print("...")
            i = int(input("Number of layers in NN: (3):"))
            if i < 2:
                print("Number of layers should be bigger than 2")
                i = 0
            net_size = []
            for j in range(i):
                if j == 0:
                    print("Size of the input layer is 2")
                    continue
                if j == i - 1:
                    print("Size of the output layer is 2")
                    continue
                curr = int(input("Number of neurons in this layer:"))
                net_size.append(curr)
            generation_size_default = int(input("Enter the size of one generation (800):"))
            food_spawn_chance = int(input("For a chance for new food to appear 1/n, enter new n (100):"))
            wolf_spawn_chance = int(input("For a chance for new wolf to appear 1/n, enter new n (70):"))
            mutation_props = int(input("For a chance for weight/bias to mutate being 1/n, enter new n (50)"))
            print("...")
            print("Download source code for the ability to change more.")
            print("https://github.com/urhprimozic/smart-sheep")
            print()
            buttons[2].string = "Settings"
        if event == 13:
            if buttons[3].string == "Stop music":
                pygame.mixer.music.pause()
                buttons[3].string = "Start music"
            else:
                pygame.mixer.music.unpause()
                buttons[3].string = "Stop music"



    americano_active = False


americano()

