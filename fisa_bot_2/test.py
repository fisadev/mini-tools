# coding: utf-8
from datetime import datetime
from pytron_fisa import *
from random import randint


class BotStatus(object):
    def __init__(self, number, bot, x, y, direction):
        self.number = number
        self.bot = bot
        self.x = x
        self.y = y
        self.direction = direction


def display_arena(arena):
    print '\n'.join(''.join(str(int(cell)) if cell else ' '
                            for cell in row)
                    for row in arena.transpose())


size = 32

arena = numpy.zeros((size, size))

bots = [BotStatus(1, MyLightCycleBot(), randint(0, size), randint(0, size), None),
        BotStatus(2, MyLightCycleBot(), randint(0, size), randint(0, size), None)]

for b in bots:
    arena[b.x, b.y] = b.number

play = True
while play:
    for b in bots:
        display_arena(arena)

        start = datetime.now()
        action = b.bot.get_next_step(arena, b.x, b.y, b.direction)
        end = datetime.now()
        print b.number, 'action', action, 'in', end - start

        dx, dy = MyLightCycleBot.ACTIONS[action]
        b.x += dx
        b.y += dy
        b.direction = action
        if arena[b.x, b.y] != 0 or not (0 <= b.x < size) or not (0 <= b.y < size):
            play = False
            print b.number, 'crashed!'

        arena[b.x, b.y] = b.number

        raw_input()
