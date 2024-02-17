import matplotlib.pyplot as plt
import numpy as np
import pygame, random

pygame.init()
pygame.display.set_caption('Humans versus zombies')

WIN_SIZE = (1000, 750)
WINDOW = pygame.display.set_mode(WIN_SIZE)

NB_ENTITIES = 175
NB_GEN = 100

class Entity:
    def __init__(self, color, position, sense, speed):
        self.color = color
        self.position = position
        self.sense = sense
        self.speed = speed

    def closest_entity(self, entities):
        min = (0, np.inf)
        for i, entity in enumerate(entities):
            distance = np.square(self.position[0] - entity.position[0]) + np.square(self.position[1] - entity.position[1])
            if distance < min[1]: min = (i, distance)

        return (entities[min[0]], np.sqrt(min[1]))

    def move(self, x, y):
        self.position = (
            (self.position[0] - x*self.speed) % WIN_SIZE[0],
            (self.position[1] - y*self.speed) % WIN_SIZE[1]
        )
        pygame.draw.circle(WINDOW, self.color, self.position, 3)

class Human(Entity):
    def __init__(self, sense, shoot_precision, speed):
        self.life = 0
        self.shoot_precision = shoot_precision
        super().__init__(
            (0, 0, 255),
            (random.randint(0, WIN_SIZE[0]), random.randint(0, WIN_SIZE[1])),
            sense, speed
        )

    def actions(self):
        self.life += 1
        if zombies:
            zombie, distance = self.closest_entity(zombies)

            if distance < self.sense/2:
                if random.random() < self.shoot_precision/3: zombie.killed()
            elif distance < self.sense:
                super().move(
                    np.sign(zombie.position[0] - self.position[0]),
                    np.sign(zombie.position[1] - self.position[1])
                )
            else: super().move(random.choice((-1, 1)), random.choice((-1, 1)))

    def death(self):
        deaths.append(self)
        humans.remove(self)

class Zombie(Entity):
    def __init__(self, position, sense=15, speed=7):
        super().__init__((0, 255, 0), position, sense, speed)

    def actions(self):
        if humans:
            human, distance = self.closest_entity(humans)

            if distance < 2: self.eat(human)
            else:
                super().move(
                    np.sign(self.position[0] - human.position[0]),
                    np.sign(self.position[1] - human.position[1])
                )

    def eat(self, human):
        zombies.append(Zombie(human.position, human.sense, human.speed))
        human.death()

    def killed(self): zombies.remove(self)

def actions():
    entities = (humans, zombies) if random.random() < 0.5 else (zombies, humans)
    for entity in entities[0]: entity.actions()
    for entity in entities[1]: entity.actions()

def init_humans(nb=NB_ENTITIES):
    return [Human(
        random.randint(4, 20),
        random.random(),
        random.randint(3, 12),
    ) for _ in range(nb)]

def init_zombies():
    return [Zombie(
        (random.randint(0, WIN_SIZE[0]), random.randint(0, WIN_SIZE[1]))
    ) for _ in range(NB_ENTITIES)]

def natural_selection():
    dead_humans = sorted(deaths, key=lambda d: d.life, reverse=True)
    humans = [
        Human(dead_human.sense, dead_human.shoot_precision, dead_human.speed)
        for dead_human in dead_humans if random.random() <= dead_human.life / dead_humans[0].life
    ]
    humans.extend(init_humans(NB_ENTITIES - len(humans)))
    return humans

def progress_bar(progres, total):
    percent = (progres/float(total))*100
    bar = '█'*int(percent) + '-'*(100-int(percent))
    return f'|{bar}| {percent:.2f}%'

axis = []
isPlaying = True
nb_gen = 0
stats = {'sense':[], 'shoot_precision':[], 'speed':[]}

print(progress_bar(0, NB_GEN), end='\r')
while nb_gen < NB_GEN and isPlaying:
    humans = init_humans() if nb_gen == 0 else natural_selection()
    deaths = []
    zombies = init_zombies()

    i = 0
    while humans and zombies and i < NB_ENTITIES and isPlaying:
        WINDOW.fill((0,0,0))
        for event in pygame.event.get():
            isPlaying = not (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE))
        actions()
        i += 1
        pygame.display.flip()

    if humans:
        winners = f'Humans won, {len(humans)} were still alive'
        for human in humans:
            human.life += 100
            human.death()
    else: winners = f'Zombies won, {len(zombies)} were still alive'

    axis.append(nb_gen)
    for key in stats.keys(): stats[key].append(np.average([getattr(human, key) for human in deaths]))

    nb_gen += 1
    print(progress_bar(nb_gen, NB_GEN), '\t', winners, end='\r')

print('\n')

pygame.quit()

plt.xlabel('Generation')
plt.ylabel('Gene average')

m, b = np.polyfit(axis, stats['speed'], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(axis, aj_lineaire(axis), label='speed', color='#294DBA')
plt.plot(axis, stats['speed'], label='speed Point', color='#1B327A', alpha=0.2)

m, b = np.polyfit(axis, stats['sense'], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(axis, aj_lineaire(axis), label='sense', color='#9AFA1E')
plt.plot(axis, stats['sense'], label='sense Point', color='#6FAD1D', alpha=0.2)

m, b = np.polyfit(axis, stats['shoot_precision'], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(axis, aj_lineaire(axis), label='shoot precision', color='#FA9D43')
plt.plot(axis, stats['shoot_precision'], label='shoot precision Point', color='#AD7237', alpha=0.2)

plt.legend(loc='upper left')
plt.show()
