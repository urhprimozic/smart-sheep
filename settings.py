# Neural net. Every element represent a new layer, and its value number of neurons in that layer.
# Output layer should have the value of 2
net_size = [2, 3, 2]
# number of sheeps in one generation
# generation_size = 800
# value of 1 eaten package of food (for the fitness function)
food_value = 10
# value of 1 step staying alive (for the fitness function)
step_value = 0
# value ... when jumping over a wolf
wolf_value = 100
# gravitational acceleration
g = 1
# wolf's speed
wolf_speed = -10
# speed for food packages
food_speed = -8
# acceleration when jumping (F/m)
sheep_jump = -19
# speed of animation
anime_speed = 2
# window sizes
height = 400  # Default settings. Window is resizable
width = 800
log_width = 600
# Colors
white = 255, 255, 255
black = 0, 0, 0
gray = 180, 180, 180
background_color = [255.0, 255.0, 255.0]
# value, by which  background color is changed every step
color_change = 0.01
# ground (position)
ground_y = height - 30
# (chance of new food spawning)^1
food_spawn_chance = 100
# chance of new wolf spawning ^1
wolf_spawn_chance = 70
# hunger, that kills a speeh
max_hunger = 1000
# value, by which hunger is raised every step
hunger_value = 0.1
# chance of mutation ^ 1
mutation_props = 50
# generation_size_default = 800


## gg
## gg
## gg
## gg

class country_of_peace:
    def __init__(self):
        self.ego = -1  # owerflow

    def invade_with_guns(self):
        os._exit(1)
