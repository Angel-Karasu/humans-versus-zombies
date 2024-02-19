import matplotlib.pyplot as plt
import numpy as np
import random

DISPLAY = True
NB_ENTITIES = 750
NB_GEN = 24*365              # Simulating one year of generations
WORLD_SIZE = (1280, 720)     # in m²

if DISPLAY:
    import pygame

    pygame.init()
    pygame.display.set_caption('Humans versus zombies')
    pygame.font.init()
    FONT = pygame.font.SysFont('DejaVu Sans', 10)
    WINDOW = pygame.display.set_mode(WORLD_SIZE)

class Entity:
    def __init__(self, color:tuple[int, 3], position:tuple[int, 2], sense: int, speed: int):
        self.color = color
        self.position = position
        self.sense = sense # In m
        self.speed = speed # In m/s

    def move(self, x:int, y:int):
        self.position = (
            (self.position[0] - x*self.speed) % WORLD_SIZE[0],
            (self.position[1] - y*self.speed) % WORLD_SIZE[1]
        )
        if DISPLAY: pygame.draw.circle(WINDOW, self.color, self.position, 1)

class Human(Entity):
    def __init__(self, sense:int, shoot_precision:float, speed:int):
        self.survive_time = 1 # In second
        self.shoot_precision = shoot_precision
        super().__init__(
            (0, 0, 255),
            (random.randint(0, WORLD_SIZE[0]), random.randint(0, WORLD_SIZE[1])),
            sense, speed
        )

    def actions(self, zombie:'Zombie', distance:float):
        self.survive_time += 1 # Add 1 second
        if distance < self.sense/2:
            if random.random() < self.shoot_precision: zombie.death()
        elif distance < self.sense:
            super().move(
                np.sign(zombie.position[0] - self.position[0]),
                np.sign(zombie.position[1] - self.position[1])
            )
        else: super().move(random.choice((-1, 1)), random.choice((-1, 1)))

    def death(self):
        global deaths, humans
        deaths = np.append(deaths, [self])
        humans = np.delete(humans, np.where(humans == self))

class Zombie(Entity):
    def __init__(self, position:tuple[int, 2], sense:int, speed:int):
        super().__init__((0, 255, 0), position, sense, speed)

    def actions(self, human:Human, distance:float):
        if distance < 2: self.eat(human)
        elif distance < self.sense:
            super().move(
                np.sign(self.position[0] - human.position[0]),
                np.sign(self.position[1] - human.position[1])
            )
        else: super().move(random.choice((-1, 1)), random.choice((-1, 1)))

    def eat(self, human):
        np.append(zombies, Zombie(human.position, human.sense, human.speed))
        human.death()

    def death(self):
        global zombies
        zombies = np.delete(zombies, np.where(zombies == self))

def actions():
    entities = (humans, zombies) if len(humans) > len(zombies) else (zombies, humans)
    for entity1 in entities[0]:
        if entities[1].any():
            entity2, distance = closest_entity(entity1, entities[1])
            if random.random() > 0.5: entity1.actions(entity2, distance)
            else: entity2.actions(entity1, distance)

def closest_entity(entity:Entity, entities:np.ndarray[Entity]):
    entities_position = np.array([entity.position for entity in entities])
    distances = np.sum(np.square(entities_position - np.array(entity.position)), axis=1)
    closest_index = np.argmin(distances)
    
    return entities[closest_index], np.sqrt(distances[closest_index])

def init_humans(nb=NB_ENTITIES) -> np.ndarray[Human]:
    return np.array([Human(
        random.randint(10, 15),
        random.random()/2,
        random.randint(2, 8)
    ) for _ in range(nb)])

def init_zombies() -> np.ndarray[Zombie]:
    return np.array([Zombie(
        (random.randint(0, WORLD_SIZE[0]), random.randint(0, WORLD_SIZE[1])),
        random.randint(10, 25),
        random.randint(2, 6)
    ) for _ in range(NB_ENTITIES)])

def natural_selection() -> np.ndarray[Human]:
    dead_humans = sorted(deaths, key=lambda d: d.survive_time, reverse=True)
    humans = np.array([
        Human(dead_human.sense, dead_human.shoot_precision, dead_human.speed)
        for dead_human in dead_humans if random.random() <= dead_human.survive_time / dead_humans[0].survive_time
    ])
    return np.append(humans, init_humans(NB_ENTITIES - len(humans)))

def progress_bar(progres, total):
    percent = (progres/float(total))*100
    bar = '█'*int(percent) + '-'*(100-int(percent))
    return f'|{bar}| {percent:.2f}%'

is_running = True
nb_gen = 0
stats = {'sense':[], 'shoot_precision':[], 'speed':[]}

print(progress_bar(0, NB_GEN), end='\r')
while nb_gen < NB_GEN and is_running:
    humans = init_humans() if nb_gen == 0 else natural_selection()
    deaths = np.array([])
    zombies = init_zombies()

    time = 0
    while humans.any() and zombies.any() and time < 3600 and is_running: # Simulate one hour
        if DISPLAY:
            for event in pygame.event.get([pygame.QUIT, pygame.KEYDOWN]):
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) :is_running = False
            WINDOW.fill((0,0,0))
            for i, text in enumerate([f'Nb gene : {nb_gen}/{NB_GEN}', f'Survive time : {time}s', f'Humans : {len(humans)}', f'Zombies : {len(zombies)}']):
                WINDOW.blit(FONT.render(text, False, (255, 255, 255)), (5,5+i*15))
            actions()
            pygame.display.flip()
        else: actions()
        time += 1 # Add 1 second

    if humans.any():
        winners = f'Humans won, {len(humans)} were still alive'
        for human in humans:
            human.survive_time *= 2
            human.death()
    else: winners = f'Zombies won, {len(zombies)} were still alive'

    for key in stats.keys(): stats[key].append(np.average([getattr(human, key) for human in deaths]))

    nb_gen += 1
    print(progress_bar(nb_gen, NB_GEN), '\t', winners, end='\r')

print('\n')

if DISPLAY: pygame.quit()

axis = np.arange(nb_gen)

fig, ax1 = plt.subplots()
ax1.set_xlabel('Nb generation')

ax1.set_ylabel('speed (m/s)', color='#213757')
ax1.plot(axis, stats['speed'], color='#213757')
ax1.tick_params(axis='y', labelcolor='#213757')

ax2 = ax1.twinx()
ax2.set_ylabel('sense (m)', color='#3DA542')
ax2.plot(axis, stats['sense'], color='#3DA542')
ax2.tick_params(axis='y', labelcolor='#3DA542')

ax3 = ax1.twinx()
ax3.set_ylabel('shoot precision', color='#E38D00')
ax3.plot(axis, stats['shoot_precision'], color='#E38D00')
ax3.tick_params(axis='y', labelcolor='#E38D00')

fig.tight_layout()
plt.show()