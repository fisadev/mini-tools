"""
Made to solve the mayhem version of this challenge:
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

# state representation: (circuit, previous_position, position, (coat, hat, belt, boots, tutu, left_glove, right_golve))
INITIAL = '', None, 'S', (0, 0, 0, 0, 0, 0, 0)
GOAL_CLOTHES = (1, 1, 1, 1, 0, 1, 1)

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
        circuit, previous_position, position, clothes = state
        # goal is reaching the end with the desired clothes
        return position == 'E' and clothes == GOAL_CLOTHES

    def cost(self, state1, action, state2):
        # all actions cost the same
        return 1

    def actions(self, state):
        circuit, previous_position, position, clothes = state
        # can move to the connected rooms
        possible_actions = list(CONNECTIONS[position])
        # but we must avoid returning to the previous room
        if previous_position in possible_actions:
            possible_actions.remove(previous_position)

        return possible_actions

    def result(self, state, action):
        circuit, previous_position, position, clothes = state

        # move to the new room
        previous_position = position
        position = action
        circuit += action

        # apply dressing changes
        clothes = list(clothes)

        # basic changes based on room
        changes_to_apply = list(CHANGES[position])

        # glove changes based on circuits
        if circuit.endswith('A'):
            inner_circuit = circuit[:-1]
            if inner_circuit.startswith('B') and inner_circuit.endswith('D'):
                # westward circuit completed
                # change left glove
                changes_to_apply.append(5)
            elif inner_circuit.startswith('D') and inner_circuit.endswith('B'):
                # eastward circuit completed
                # change right glove
                changes_to_apply.append(6)

            circuit = ''  # reset circuit

        # apply all detected changes
        for change in changes_to_apply:
            if clothes[change] == 0:
                clothes[change] = 1
            else:
                clothes[change] = 0

        return circuit, previous_position, position, tuple(clothes)

    def heuristic(self, state):
        circuit, previous_position, position, clothes = state
        estimation = 0
        # needs to do at least one movement if the position is not the goal one
        if position != 'E':
            estimation += 1

        # needs to do at least one movement for each pair of things to change
        # (because it can change up to 2 things in one action)
        pending_changes = sum(1 for in_state, in_goal in zip(clothes, GOAL_CLOTHES)
                              if in_state != in_goal)
        estimation += pending_changes / 2

        return estimation


result = astar(SantaProblem(INITIAL), graph_search=True)

for action, state in result.path():
    circuit, previous_position, position, clothes = state
    print(position, clothes)
