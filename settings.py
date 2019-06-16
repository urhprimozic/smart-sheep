# Neural net. Every element represent a new layer, and its value number of neurons in that layer.
# Output layer should have the value of 2
net = [2, 3, 2]
# number of sheeps in one generation
generation_size = 800
# value of 1 eaten package of food (for the fitness function)
food_value = 1000
# value of 1 step staying alive (for the fitness function)
step_value = 0.001
# gravitational acceleration
g = 1
# wolf's speed
wolf_speed = -10
# speed for food packages
food_speed = -8
# acceleration when jumping (F/m)
sheep_jump = -18
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
food_spawn_chance = 90
# chance of new wolf spawning ^1
wolf_spawn_chance = 55
# hunger, that kills a speeh
max_hunger = 10000
# value, by which hunger is raised every step
hunger_value = 0.1
