import matplotlib.pyplot as plt
import numpy as np
import random

DISPLAY = True
NB_ENTITIES = 250
NB_GEN = 24*365             # Simulating a year of generations
WORLD_SIZE = (1600, 900)    # World 1600*900 m²

if DISPLAY:
    import pygame

    pygame.init()
    pygame.display.set_caption('Humans versus zombies')
    pygame.event.set_allowed((pygame.QUIT, pygame.KEYDOWN))
    WINDOW = pygame.display.set_mode(WORLD_SIZE)

class Entity:
    def __init__(self, color:tuple[int, 3], position:tuple[int, 2], sense: int, speed: int):
        self.color = color
        self.position = position
        self.sense = sense
        self.speed = speed # In m/s

    def move(self, x:int, y:int):
        self.position = (
            (self.position[0] - x*self.speed) % WORLD_SIZE[0],
            (self.position[1] - y*self.speed) % WORLD_SIZE[1]
        )
        if DISPLAY: pygame.draw.circle(WINDOW, self.color, self.position, 1)

class Human(Entity):
    def __init__(self, sense:int, shoot_precision:float, speed:int):
        self.survive_time = 0 # In second
        self.shoot_precision = shoot_precision
        super().__init__(
            (0, 0, 255),
            (random.randint(0, WORLD_SIZE[0]), random.randint(0, WORLD_SIZE[1])),
            sense, speed
        )

    def actions(self, zombie:'Zombie', distance:float):
        self.survive_time += 1 # Add 1 second
        if distance < self.sense/2:
            if random.random() < self.shoot_precision/2: zombie.death()
        elif distance < self.sense: super().move(
                np.sign(zombie.position[0] - self.position[0]),
                np.sign(zombie.position[1] - self.position[1])
            )
        else: super().move(random.choice((-1, 1)), random.choice((-1, 1)))

    def death(self):
        deaths.append(self)
        humans.remove(self)

class Zombie(Entity):
    def __init__(self, position:tuple[int, 2], sense:int, speed:int):
        super().__init__((0, 255, 0), position, sense, speed)

    def actions(self, human:Human, distance:float):
        if distance < 2: self.eat(human)
        else:
            super().move(
                np.sign(self.position[0] - human.position[0]),
                np.sign(self.position[1] - human.position[1])
            )

    def eat(self, human):
        zombies.append(Zombie(human.position, human.sense, human.speed))
        human.death()

    def death(self): zombies.remove(self)

def actions():
    entities = (humans, zombies) if len(humans) > len(zombies) else (zombies, humans)
    for entity1 in entities[0]:
        if entities[1]:
            entity2, distance = closest_entity(entity1, entities[1])
            entity = (entity1, entity2) if random.random() > 0.5 else (entity2, entity1)
            entity[0].actions(entity[1], distance)
            entity[1].actions(entity[0], distance)

def closest_entity(entity1:Entity, entities:list[Entity]):
    min = (0, np.inf)
    for i, entity2 in enumerate(entities):
        distance = np.square(entity1.position[0] - entity2.position[0]) + np.square(entity1.position[1] - entity2.position[1])
        if distance < min[1]: min = (i, distance)

    return (entities[min[0]], np.sqrt(min[1]))

def init_humans(nb=NB_ENTITIES):
    return [Human(
        random.randint(4, 20),
        random.random(),
        random.randint(2, 7)
    ) for _ in range(nb)]

def init_zombies():
    return [Zombie(
        (random.randint(0, WORLD_SIZE[0]), random.randint(0, WORLD_SIZE[1])),
        random.randint(4, 15),
        random.randint(1, 4)
    ) for _ in range(NB_ENTITIES)]

def natural_selection():
    dead_humans = sorted(deaths, key=lambda d: d.survive_time, reverse=True)
    humans = [
        Human(dead_human.sense, dead_human.shoot_precision, dead_human.speed)
        for dead_human in dead_humans if random.random() <= dead_human.survive_time / dead_humans[0].survive_time
    ]
    humans.extend(init_humans(NB_ENTITIES - len(humans)))
    return humans

def progress_bar(progres, total):
    percent = (progres/float(total))*100
    bar = '█'*int(percent) + '-'*(100-int(percent))
    return f'|{bar}| {percent:.2f}%'

axis = []
is_running = True
nb_gen = 0
stats = {'sense':[], 'shoot_precision':[], 'speed':[]}

# print(progress_bar(0, NB_GEN), end='\r')
while nb_gen < NB_GEN and is_running:
    humans = init_humans() if nb_gen == 0 else natural_selection()
    deaths = []
    zombies = init_zombies()

    i = 0
    while humans and zombies and i < 3600 and is_running: # Simulate one hour
        if DISPLAY:
            WINDOW.fill((0,0,0))
            for event in pygame.event.get():
                print(event)
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): is_running = False
            actions()
            pygame.display.flip()
        else: actions()
        i += 1 # Add 1 second

    if humans:
        winners = f'Humans won, {len(humans)} were still alive'
        for human in humans:
            human.survive_time *= 2
            human.death()
    else: winners = f'Zombies won, {len(zombies)} were still alive'

    axis.append(nb_gen)
    for key in stats.keys(): stats[key].append(np.average([getattr(human, key) for human in deaths]))

    nb_gen += 1
    # print(progress_bar(nb_gen, NB_GEN), '\t', winners, end='\r')

print('\n')

if DISPLAY: pygame.quit()

plt.xlabel('Generation')
plt.ylabel('Gene average')

m, b = np.polyfit(axis, stats['speed'], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(axis, aj_lineaire(axis), label='speed', color='#62AFDE')
plt.plot(axis, stats['speed'], label='speed Point', color='#213757', alpha=0.2)

m, b = np.polyfit(axis, stats['sense'], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(axis, aj_lineaire(axis), label='sense', color='#A8D379')
plt.plot(axis, stats['sense'], label='sense Point', color='#3DA542', alpha=0.2)

m, b = np.polyfit(axis, stats['shoot_precision'], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(axis, aj_lineaire(axis), label='shoot precision', color='#ECCD00')
plt.plot(axis, stats['shoot_precision'], label='shoot precision Point', color='#E38D00', alpha=0.2)

plt.legend(loc='upper left')
plt.show()
