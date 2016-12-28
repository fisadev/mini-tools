"""
Made to solve the merry version of this challenge:
http://www.mathistopheles.co.uk/2016/12/23/the-indisputable-santa-mathematical-advent-calendarday-23/#top
"""

from simpleai.search import SearchProblem, astar
from simpleai.search.viewers import ConsoleViewer


CONNECTIONS = {
    'S': 'A',  # S is the start location
    'A': 'BDE',
    'B': 'ACD',
    'C': 'BD',
    'D': 'ABC',
    'E': '',  # E is the end location
}

# state representation: (previous_position, position, (coat, hat, belt, boots, tutu))
INITIAL = None, 'S', (0, 0, 0, 0, 0)
GOAL = 'A', 'E', (1, 1, 1, 1, 0)

# clothe changes
CHANGES = {
    'S': tuple(),  # nothing
    'E': tuple(),  # nothing
    'A': (2, 4),  # belt, tutu
    'B': (0, 4),  # coat, tutu
    'C': (1, ),  # hat
    'D': (3, ),  # boots
}


class SantaProblem(SearchProblem):
    def is_goal(self, state):
        # goal is a known state
        return state == GOAL

    def cost(self, state1, action, state2):
        # all actions cost the same
        return 1

    def actions(self, state):
        previous_position, position, clothes = state
        # can move to the connected rooms
        possible_actions = list(CONNECTIONS[position])
        # but we must avoid returning to the previous room
        if previous_position in possible_actions:
            possible_actions.remove(previous_position)

        return possible_actions

    def result(self, state, action):
        previous_position, position, clothes = state

        # move to the new room
        previous_position = position
        position = action

        # apply dressing changes
        clothes = list(clothes)
        for change in CHANGES[position]:
            if clothes[change] == 0:
                clothes[change] = 1
            else:
                clothes[change] = 0

        return previous_position, position, tuple(clothes)

    def heuristic(self, state):
        estimation = 0
        # needs to do at least one movement if the position is not the goal one
        if state[1] != GOAL[1]:
            estimation += 1

        # needs to do at least one movement for each pair of things to change
        # (because it can change up to 2 things in one action)
        pending_changes = sum(1 for in_state, in_goal in zip(state[2], GOAL[2])
                              if in_state != in_goal)
        estimation += pending_changes / 2

        return estimation


result = astar(SantaProblem(INITIAL), graph_search=True)

for action, state in result.path():
    print(state)
