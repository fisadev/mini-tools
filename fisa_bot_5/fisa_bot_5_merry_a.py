"""
Incorrect solution! (missinterpreted rules)
Check the merry_correct and mayhem versions to see both correct solutions.
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

# state representation: (position, (coat, hat, belt, boots, tutu))
INITIAL = 'S', (0, 0, 0, 0, 0)
GOAL = 'E', (1, 1, 1, 1, 0)

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
        # can move to the connected rooms
        return list(CONNECTIONS[state[0]])

    def result(self, state, action):
        position, clothes = state

        # move to the new room
        position = action

        # apply dressing changes
        clothes = list(clothes)
        for change in CHANGES[position]:
            if clothes[change] == 0:
                clothes[change] = 1
            else:
                clothes[change] = 0

        return position, tuple(clothes)

    def heuristic(self, state):
        estimation = 0
        # needs to do at least one movement if the position is not the goal one
        if state[0] != GOAL[0]:
            estimation += 1

        # needs to do at least one movement for each pair of things to change
        # (because it can change up to 2 things in one action)
        pending_changes = sum(1 for in_state, in_goal in zip(state[1], GOAL[1])
                              if in_state != in_goal)
        estimation += pending_changes / 2

        return estimation


result = astar(SantaProblem(INITIAL), graph_search=True)

for action, state in result.path():
    print(state)
