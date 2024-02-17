import random, time
import matplotlib.pyplot as plt
import numpy as np

DISTANCE_SONG = 5
NB_ENTITIES = 175
NB_GEN = 100
WORLD_AREA = 50
ZOMBIE_SPEED = 5

def progress_bar(progres, total):
    percent = (progres/float(total))*100
    bar = '█'*int(percent) + '-'*(100-int(percent))
    return f'|{bar}| {percent:.2f}%'

def average(gen, human):
    return sum(stats[gen] for _, stats in human.items())/len(human)

def init_humans(humans = {}, nb = NB_ENTITIES):
    rd = [random.randint(0, WORLD_AREA), random.randint(0, WORLD_AREA)]
    for i in range(len(humans), nb+len(humans)):
        humans[f'human {i+1}'] = {
                'speed': random.randint(1, 10),
                'vision': random.randint(1, 10),
                'precision': random.randint(1, 10),
                'position': rd,
                'song_area': [rd, rd],
                'birth': time.time(),
            }
    return humans

def init_zombies():
    zombies = []
    zombies.extend(
        [random.randint(0, WORLD_AREA), random.randint(0, WORLD_AREA)]
        for _ in range(NB_ENTITIES)
    )
    return zombies

def add_death_list(death_liste, stats):
    death_liste.append({
        'speed': stats['speed'],
        'vision': stats['vision'],
        'precision': stats['precision'],
        'time': (time.time() - stats['birth'])*1000
    })
    return death_liste

def coord_world(coord, speed):
    if coord[0] > WORLD_AREA: coord[0] -= 2*speed
    elif coord[0] < 0: coord[0] += 2*speed

    if coord[1] > WORLD_AREA: coord[1] -= 2*speed
    elif coord[1] < 0: coord[1] += 2*speed
    
    return [round(coord[0], 2), round(coord[1], 2)]

def humans_actions(humans, zombies):
    for human, stats in humans.items():
        pos = stats['position']
        song_area = [[pos[0], pos[1]], [pos[0], pos[1]]]
        speed = stats['speed']
        vision = stats['vision']
        for x, zombie in enumerate(zombies):
            coord = [pos[0] - zombie[0], pos[1] - zombie[1]]
            if abs(coord[0]) <= vision and abs(coord[1]) <= vision:
                if random.randint(1, 10)/2 <= stats['precision']/3: del zombies[x]
                song_area = [
                    [song_area[0][0] - DISTANCE_SONG, song_area[0][1] - DISTANCE_SONG],
                    [song_area[1][0] + DISTANCE_SONG, song_area[1][1] + DISTANCE_SONG],
                ]

                humans[human]['position'] = [
                    pos[0] + ((coord[0]/abs(coord[0] + 10**(-10)))*speed),
                    pos[1] + ((coord[1]/abs(coord[1] + 10**(-10)))*speed),
                ]
                break
        if humans[human]['position'] == pos:
            humans[human]['position'] = [
                pos[0] + random.choice((-1, 1))*speed,
                pos[1] + random.choice((-1, 1))*speed,
            ]

        humans[human]['position'] = coord_world(humans[human]['position'], speed)

        song_area = [
            [song_area[0][0] - 1.5*speed, song_area[0][1] - 1.5*speed],
            [song_area[1][0] + 1.5*speed, song_area[1][1] + 1.5*speed],
        ]
        humans[human]['song_area'] = song_area
    return [humans, zombies]

def zombies_actions(humans, zombies, death_list):
    for x, zombie in enumerate(zombies):
        hum = humans.copy()
        for human, stats in hum.items():
            pos = stats['position']
            song_area = stats['song_area']
            coord = [zombie[0] - pos[0], zombie[1] - pos[1]]

            if abs(coord[0]) <= 1 and abs(coord[1]) <= 1:
                zombies.append([pos[0], pos[1]])
                death_list = add_death_list(death_list, stats)
                humans.pop(human)
            elif song_area[0][0] <= zombie[0] <= song_area[1][0] and song_area[0][1] <= zombie[1] <= song_area[1][1]:
                zombies[x] = [
                    pos[0] + ((coord[0]/abs(coord[0] - 10**(-10)))*ZOMBIE_SPEED),
                    pos[1] + ((coord[1]/abs(coord[1] - 10**(-10)))*ZOMBIE_SPEED),
                ]
        
        if zombies[x] == zombie:
            zombies[x] = [zombie[0] + random.choice((-1, 1))*ZOMBIE_SPEED, zombie[1] + random.choice((-1, 1))*ZOMBIE_SPEED]
            
        zombies[x] = coord_world(zombies[x], ZOMBIE_SPEED)

    return [humans, zombies, death_list]

def actions(humans, zombies, death_list):
    if random.random() >= 0.5:
        humans, zombies = humans_actions(humans, zombies)
        humans, zombies, death_list = zombies_actions(humans, zombies, death_list)
    else:
        humans, zombies, death_list = zombies_actions(humans, zombies, death_list)
        humans, zombies = humans_actions(humans, zombies)
    
    return [humans, zombies, death_list]

def kill_human(humans, death_list):
    for _, stats in humans.items():
        death_list = add_death_list(death_list, stats)
    return death_list

def create_new_gen(death_list):
    humans = {}
    total_time = sum(death['time'] for death in death_list)
    death_list = sorted(death_list, key=lambda t: t['time'], reverse=True)

    for i in range((NB_ENTITIES*3)//5):
        rand = random.random()
        last_prob = 0

        for gen in death_list:
            prob = gen['time']/total_time
            if rand >= last_prob and rand < prob + last_prob:
                rd = [random.randint(0, WORLD_AREA), random.randint(0, WORLD_AREA)]
                humans[f'human {i+1}'] = {
                    'speed': gen['speed'],
                    'vision': gen['vision'],
                    'precision': gen['precision'],
                    'position': rd,
                    'song_area': [rd, rd],
                    'birth': time.time(),
                }
                break
            last_prob += prob
    humans |= init_humans(humans, (NB_ENTITIES*2)//5)
    return humans

print(progress_bar(0, NB_GEN), end='\r')
humans = init_humans()
l = []
stats = ['speed', 'vision', 'precision']
stats_list = [[], [] , []]

for i in range(NB_GEN):
    l.append(i)
    for x in range(len(stats)): stats_list[x].append(average(stats[x], humans))

    zombies = init_zombies()
    death_list = []
    k = 0
    while len(humans) > 0 and len(zombies) > 0 and k < 2*(WORLD_AREA + NB_ENTITIES):
        humans, zombies, death_list = actions(humans, zombies, death_list)
        k += 1

    if len(humans) > 0:
        winners = f'Humans won, {len(humans)} were still alive'
        death_list = kill_human(humans, death_list)
    else: winners = f'Zombies won, {len(zombies)} were still alive'

    humans = create_new_gen(death_list)
    print(progress_bar(i+1, NB_GEN), '\t', winners, end='\r')
print('\n')


plt.xlabel('Generation')
plt.ylabel('Gene average')

m, b = np.polyfit(l, stats_list[0], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(l, aj_lineaire(l), label='speed', color='#294DBA')
plt.plot(l, stats_list[0], label='speed Point', color='#1B327A', alpha=0.2)

m, b = np.polyfit(l, stats_list[1], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(l, aj_lineaire(l), label='vision', color='#9AFA1E')
plt.plot(l, stats_list[1], label='vision Point', color='#6FAD1D', alpha=0.2)

m, b = np.polyfit(l, stats_list[2], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(l, aj_lineaire(l), label='Précision', color='#FA9D43')
plt.plot(l, stats_list[2], label='Précision Point', color='#AD7237', alpha=0.2)

plt.legend(loc='upper left')
plt.show()
