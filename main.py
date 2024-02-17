import random, time
import matplotlib.pyplot as plt
import numpy as np

nb = 175
monde = 50
son = 5
vitZomb = 5

def barreProgression(progres, total):
    pourcent = (progres/float(total))*100
    barre = '█'*int(pourcent) + '-'*(100-int(pourcent))
    return f'|{barre}| {pourcent:.2f}%'

def moyenne(gen ,population):
    return sum(stats[gen] for _, stats in population.items())/len(population)

def creerPopulation(population = {}, nb = nb):
    rd = [random.randint(0, monde), random.randint(0, monde)]
    for i in range(len(population), nb+len(population)):
        population[f'humain {i+1}'] = {
                'vitesse': random.randint(1, 10),
                'vue': random.randint(1, 10),
                'precision': random.randint(1, 10),
                'position': rd,
                'zoneBruit': [rd, rd],
                'creer': time.time(),
            }
    return population

def creerZombies():
    zombies = []
    zombies.extend(
        [random.randint(0, monde), random.randint(0, monde)]
        for _ in range(nb)
    )
    return zombies

def listeMortAppend(listeMort, stats):
    listeMort.append({
        'vitesse': stats['vitesse'],
        'vue': stats['vue'],
        'precision': stats['precision'],
        'duree': (time.time() - stats['creer'])*1000
    })
    return listeMort

def coordMap(coord, vitesse):
    if coord[0] > monde: coord[0] -= 2*vitesse
    elif coord[0] < 0: coord[0] += 2*vitesse

    if coord[1] > monde: coord[1] -= 2*vitesse
    elif coord[1] < 0: coord[1] += 2*vitesse
    
    return [round(coord[0], 2), round(coord[1], 2)]

def actionsHumain(population, zombies):
    for humain, stats in population.items():
        pos = stats['position']
        zB = [[pos[0], pos[1]], [pos[0], pos[1]]]
        vit = stats['vitesse']
        vue = stats['vue']
        for x, zombie in enumerate(zombies):
            coord = [pos[0] - zombie[0], pos[1] - zombie[1]]
            if abs(coord[0]) <= vue and abs(coord[1]) <= vue:
                if random.randint(1, 10)/2 <= stats['precision']/3: del zombies[x]
                zB = [
                    [zB[0][0] - son, zB[0][1] - son],
                    [zB[1][0] + son, zB[1][1] + son],
                ]

                population[humain]['position'] = [
                    pos[0] + ((coord[0]/abs(coord[0] + 10**(-10)))*vit),
                    pos[1] + ((coord[1]/abs(coord[1] + 10**(-10)))*vit),
                ]
                break
        if population[humain]['position'] == pos:
            population[humain]['position'] = [
                pos[0] + random.choice((-1, 1))*vit,
                pos[1] + random.choice((-1, 1))*vit,
            ]

        population[humain]['position'] = coordMap(population[humain]['position'], vit)

        zB = [
            [zB[0][0] - 1.5*vit, zB[0][1] - 1.5*vit],
            [zB[1][0] + 1.5*vit, zB[1][1] + 1.5*vit],
        ]
        population[humain]['zoneBruit'] = zB
    return [population, zombies]

def actionsZombies(population, zombies, listeMort):
    for x, zombie in enumerate(zombies):
        pop = population.copy()
        for humain, stats in pop.items():
            pos = stats['position']
            zB = stats['zoneBruit']
            coord = [zombie[0] - pos[0], zombie[1] - pos[1]]

            if abs(coord[0]) <= 1 and abs(coord[1]) <= 1:
                zombies.append([pos[0], pos[1]])
                listeMort = listeMortAppend(listeMort, stats)
                population.pop(humain)
            elif zB[0][0] <= zombie[0] <= zB[1][0] and zB[0][1] <= zombie[1] <= zB[1][1]:
                zombies[x] = [
                    pos[0] + ((coord[0]/abs(coord[0] - 10**(-10)))*vitZomb),
                    pos[1] + ((coord[1]/abs(coord[1] - 10**(-10)))*vitZomb),
                ]
        
        if zombies[x] == zombie:
            zombies[x] = [zombie[0] + random.choice((-1, 1))*vitZomb, zombie[1] + random.choice((-1, 1))*vitZomb]
            
        zombies[x] = coordMap(zombies[x], vitZomb)

    return [population, zombies, listeMort]

def actions(population, zombies, listeMort):
    if random.random() >= 0.5:
        population, zombies = actionsHumain(population, zombies)
        population, zombies, listeMort = actionsZombies(population, zombies, listeMort)
    else:
        population, zombies, listeMort = actionsZombies(population, zombies, listeMort)
        population, zombies = actionsHumain(population, zombies)
    
    return [population, zombies, listeMort]

def tuerHumain(population, listeMort):
    for _, stats in population.items():
        listeMort = listeMortAppend(listeMort, stats)
    return listeMort

def creerNouvelleGen(listeMort):
    population = {}
    tempsTotal = sum(mort['duree'] for mort in listeMort)
    listeMort = sorted(listeMort, key=lambda t: t['duree'], reverse=True)

    for i in range((nb*3)//5):
        rand = random.random()
        derniereProb = 0

        for gen in listeMort:
            prob = gen['duree']/tempsTotal
            if rand >= derniereProb and rand < prob + derniereProb:
                rd = [random.randint(0, monde), random.randint(0, monde)]
                population[f'humain {i+1}'] = {
                    'vitesse': gen['vitesse'],
                    'vue': gen['vue'],
                    'precision': gen['precision'],
                    'position': rd,
                    'zoneBruit': [rd, rd],
                    'creer': time.time(),
                }
                break
            derniereProb += prob
    population |= creerPopulation(population, (nb*2)//5)
    return population

nbGen = 1000
print(barreProgression(0, nbGen), end='\r')
population = creerPopulation()
l = []
stats = ['vitesse', 'vue', 'precision']
statsListe = [[], [] , []]

for i in range(nbGen):
    l.append(i)
    for x in range(len(stats)): statsListe[x].append(moyenne(stats[x], population))

    zombies = creerZombies()
    listeMort = []
    k = 0
    while len(population) > 0 and len(zombies) > 0 and k < 2*(monde + nb):
        population, zombies, listeMort = actions(population, zombies, listeMort)
        k += 1

    if len(population) > 0:
        vic = f'\rLes humains ont gagné, il en restait {len(population)}'
        listeMort = tuerHumain(population, listeMort)
    else: vic = f'\rLes zombies ont gagné, il en restait {len(zombies)}'

    population = creerNouvelleGen(listeMort)
    print(vic, '  ',barreProgression(i+1, nbGen), end='\r')
print('\n')


plt.xlabel('Génération')
plt.ylabel('Moyenne des gènes')

m, b = np.polyfit(l, statsListe[0], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(l, aj_lineaire(l), label='Vitesse', color='#294DBA')
plt.plot(l, statsListe[0], label='Vitesse Point', color='#1B327A', alpha=0.2)

m, b = np.polyfit(l, statsListe[1], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(l, aj_lineaire(l), label='Vue', color='#9AFA1E')
plt.plot(l, statsListe[1], label='Vue Point', color='#6FAD1D', alpha=0.2)

m, b = np.polyfit(l, statsListe[2], 1)
aj_lineaire = np.poly1d([m, b])
plt.plot(l, aj_lineaire(l), label='Précision', color='#FA9D43')
plt.plot(l, statsListe[2], label='Précision Point', color='#AD7237', alpha=0.2)

plt.legend(loc='upper left')
plt.show()
