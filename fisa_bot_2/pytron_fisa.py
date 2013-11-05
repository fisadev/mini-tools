LightCycleBaseBot=object


import numpy
import math


class MyLightCycleBot(LightCycleBaseBot):
    ACTIONS = {
        'N': (0, -1),
        'S': (0, 1),
        'W': (-1, 0),
        'E': (1, 0),
    }

    INVERSE_ACTIONS = {
        'N': 'S',
        'S': 'N',
        'W': 'E',
        'E': 'W',
        None: None,
    }

    def __init__(self):
        self.last_arena = None

    def get_next_step(self, arena, x, y, direction):
        me = x, y
        other = self.find_other(arena, me)
        actions = MyLightCycleBot.get_actions(arena, me, direction)

        self.last_arena = arena.copy()

        resulting_distance = lambda action_result: MyLightCycleBot.distance(action_result[1], other)
        actions = sorted(actions, key=resulting_distance)

        actions_with_futures = [(action, len(MyLightCycleBot.get_actions(arena, result, action)))
                                for action, result in actions]

        good_actions = [action for action, futures in actions_with_futures if futures > 1]
        if good_actions:
            return good_actions[0]

        hmmm_actions = [action for action, futures in actions_with_futures if futures > 0]
        if hmmm_actions:
            return hmmm_actions[0]

        if actions:
            return actions[0]
        else:
            return 'N'

    def find_other(self, arena, me):
        my_number = arena[me]
        if self.last_arena is None:
            self.last_arena = numpy.zeros(arena.shape)

        try:
            difference = arena - self.last_arena
            for x, y in zip(*difference.nonzero()):
                if arena[x, y] != my_number:
                    return x, y
        except:
            pass

        return arena.shape[0] / 2, arena.shape[1] / 2

    @classmethod
    def can_go(cls, arena, pos):
        x, y = pos
        return 0 <= x < arena.shape[0] and \
               0 <= y < arena.shape[1] and \
               arena[x, y] == 0

    @classmethod
    def get_actions(cls, arena, pos, direction):
        actions = [(action, cls.apply_action(pos, action))
                   for action in cls.ACTIONS
                   if cls.INVERSE_ACTIONS[direction] != action]
        return [(action, result) for action, result in actions
                 if cls.can_go(arena, result)]

    @classmethod
    def apply_action(cls, pos, action):
        x, y = pos
        dx, dy = cls.ACTIONS[action]
        return (x + dx, y + dy)

    @classmethod
    def distance(cls, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt(abs(x1 - x2)**2 + abs(y1 - y2)**2)


