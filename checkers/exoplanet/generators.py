#!/usr/bin/env python3.7

import os
import sys
import enum
import random




CURDIR = os.path.dirname(os.path.abspath(__file__))




nm1 = ["b","c","ch","d","g","h","k","l","m","n","p","r","s","t","th","v","x","y","z","","","","",""]
nm2 = ["a","e","i","o","u"]
nm3 = ["b","bb","br","c","cc","ch","cr","d","dr","g","gn","gr","l","ll","lr","lm","ln","lv","m","n","nd","ng","nk","nn","nr","nv","nz","ph","s","str","th","tr","v","z"]
nm3b = ["b","br","c","ch","cr","d","dr","g","gn","gr","l","ll","m","n","ph","s","str","th","tr","v","z"]
nm4 = ["a","e","i","o","u","a","e","i","o","u","a","e","i","o","u","ae","ai","ao","au","a","ea","ei","eo","eu","e","ua","ue","ui","u","ia","ie","iu","io","oa","ou","oi","o"]
nm5 = ["turn","ter","nus","rus","tania","hiri","hines","gawa","nides","carro","rilia","stea","lia","lea","ria","nov","phus","mia","nerth","wei","ruta","tov","zuno","vis","lara","nia","liv","tera","gantu","yama","tune","ter","nus","cury","bos","pra","thea","nope","tis","clite"]
nm6 = ["una","ion","iea","iri","illes","ides","agua","olla","inda","eshan","oria","ilia","erth","arth","orth","oth","illon","ichi","ov","arvis","ara","ars","yke","yria","onoe","ippe","osie","one","ore","ade","adus","urn","ypso","ora","iuq","orix","apus","ion","eon","eron","ao","omia"]
nm7 = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","0","1","2","3","4","5","6","7","8","9","0","1","2","3","4","5","6","7","8","9","","","","","","","","","","","","","",""]


def star_name():
    case = random.randint(0, 4)
	
    if case == 0:
        rnd = random.choice(nm1)
        rnd2 = random.choice(nm2)
        rnd3 = random.choice(nm3)
        while rnd == rnd3:
            rnd3 = random.choice(nm3)
        rnd4 = random.choice(nm4)
        rnd5 = random.choice(nm5)
        name = rnd + rnd2 + rnd3 + rnd4 + rnd5
	
    elif case == 1:
        rnd = random.choice(nm1)
        rnd2 = random.choice(nm2)
        rnd3 = random.choice(nm3)
        while rnd == rnd3:
            rnd3 = random.choice(nm3)
        rnd4 = random.choice(nm6)
        name = rnd + rnd2 + rnd3 + rnd4
	
    elif case == 2:
        rnd = random.choice(nm1)
        rnd4 = random.choice(nm4)
        rnd5 = random.choice(nm5)
        name = rnd + rnd4 + rnd5

    elif case == 3:
        rnd = random.choice(nm1)
        rnd2 = random.choice(nm2)
        rnd3 = random.choice(nm3b)
        while rnd == rnd3:
            rnd3 = random.choice(nm3b)
        rnd4 = random.choice(nm2)
        rnd5 = random.choice(nm5)
        name = rnd3 + rnd2 + rnd + rnd4 + rnd5

    else:
        rnd = random.choice(nm3b)
        rnd2 = random.choice(nm6)
        rnd3 = random.choice(nm7)
        rnd4 = random.choice(nm7)
        rnd5 = random.choice(nm7)
        rnd6 = random.choice(nm7)
        name = rnd + rnd2 + " " + rnd3 + rnd4 + rnd5 + rnd6

    return name.title()




with open(f'{CURDIR}/constellations.txt', 'r') as file:
    CONSTELLATIONS = [line.strip() for line in file.readlines()]


def star_location():
    return random.choice(CONSTELLATIONS)




with open(f'{CURDIR}/planets.txt', 'r') as file:
    PLANETS = [line.strip() for line in file.readlines()]


def planet_name():
    return random.choice(PLANETS)




def planet_location():
    position = random.choice(['near', 'around', 'above', 'below', 'behind', 'over', 'to', 'under', 'along', 'beneath', 'beside', 'beyond'])
    
    case = random.randint(0, 3)
    meters = random.randint(100_000_000_000, 1_000_000_000_000)

    if case == 0:
        unit = 'meters'
        power = random.randint(6, 10)
        distance = f'{meters / (10 ** power):0.4f} x 10^{power}'
    elif case == 1:
        unit = 'kilometers'
        distance = f'{meters // 1000}'
    elif case == 2:
        unit = 'light years'
        distance = f'{meters / 9_460_730_472_580_800:0.10f}'
    else:
        unit = 'parsecs'
        power = random.randint(5, 11)
        distance = f'{meters * (10 ** power) / 30_856_775_812_799_588} x 10^-{power}'

    return f'{distance} {unit} {position} the star'




class PlanetType(enum.IntEnum):
    Unknown = 0
    Terrestrial = 1
    Protoplanet = 2
    GasGiant = 3


def planet_type():
    return random.choice([
        PlanetType.Protoplanet,
        PlanetType.Terrestrial,
        PlanetType.GasGiant
    ])
