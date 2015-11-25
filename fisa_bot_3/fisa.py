from collections import defaultdict

import math
from gamebot import GameBot


DEBUG = False
ATTACK_RANGE = 1
MOVE_RANGE = 2
DEFENSE_DISTANCE = 5


def safe_call(f, *args, **kwargs):
    """
    Try to call a function. If debug is enabled, call it normally. Else, hide
    any exceptions thrown.
    """
    try:
        f(*args, **kwargs)
    except:
        if DEBUG:
            raise


def as_point(something):
    """
    Ensure something is a tuple of x, y.
    """
    if type(something) == tuple:
        return something
    else:
        return (something.x, something.y)


def distance(a, b):
    """
    Straight line distance between two things/points.
    """
    xa, ya = as_point(a)
    xb, yb = as_point(b)
    return math.sqrt((xa - xb)**2 + (ya - yb)**2)


def can_attack(a, b):
    """
    Is 'a' in attack range of 'b'?
    """
    return distance(a, b) == ATTACK_RANGE


def can_move(a, b):
    """
    Is 'a' in move range of 'b'?
    """
    return distance(a, b) < MOVE_RANGE


def distance_to(target):
    """
    Build a function able to calculate distances from things to a specific
    target.
    """
    def distance_to_target(x):
        return distance(x, target)

    return distance_to_target


def closest_to(things, target):
    """
    Get the thing which is closest to some target.
    """
    distance_to_target = distance_to(target)
    if things:
        return list(sorted(things, key=distance_to_target))[0]
    else:
        return None


def farthest_to(things, target):
    """
    Get the thing which is farthest to some target.
    """
    distance_to_target = distance_to(target)
    if things:
        return list(sorted(things, key=distance_to_target))[-1]
    else:
        return None


class Bot(GameBot):

    # Possible directions where a unit can move to
    # self.NW, self.N, self.NE, self.E, self.SE, self.S, self.SW, self.W
    # game_map : Is a python dictionary:
    #  - key = (x, y) that indicates a coordinate. x and y are integers.
    #  - value = a Tile object.
    # Tile object attributes:
    # own_hq: Boolean. Indicates that this tile is our own base
    # enemies_count: Integer. Indicate the amount of enemies in the tile
    # enemy_hq: Boolean. Indicates that the enemy HQ is present in the tile.
    # units: list of units objects currently on that tile.
    # reachable: boolean. Indicates that this tile is not a blocker.
    # x: integer. The x coordinate
    # y: integer. The y coordinate
    # Unit Object attributes:
    # x, y: integers. Analog to the x, y attributes in Tile object.
    # unit_id: integer: Indicates the id of the unit.

    # Usefull methods:
    # self.attack(tile, direction): Attack from one tile in a certain
    # direction. The direction must be one of the possible defined above.
    # self.move(unit, direction): Move a unit from its current
    # position in a certain direction. The direction must be one of the
    # possible defined above. IE: self.move(unit_id, self.N)

    def play(self, player_id, game_map):
        self.game_map = game_map

        # some definitions:
        # commander: friendly unit which is closer to our own HQ
        # explorer: friendly unit which is closer to the enemy HQ
        # invader: enemy unit which is closer to our own HQ
        self.gather_information()

        if self.army:
            if self.explorer_can_capture():
                self.capture_enemy_hq()
            else:
                if not self.commander_at_hq():
                    self.retreat_commander()

                if self.invader_arrived():
                    self.attack_invader()
                elif self.invader:
                    self.block_invader()
                else:
                    # (no visible enemies)
                    self.regroup_defense()
                    if self.enemy_hq_at:
                        self.capture_enemy_hq()
                    else:
                        self.explore()
        else:
            # just cry, no army left, let them invade us and pillage our
            # villages
            pass

    # Information related methods

    def gather_information(self):
        """
        Survey the battlefield (store useful information in instance
        variables).
        """
        # available directions
        self.adyacent_directions = (
            self.N,
            self.S,
            self.E,
            self.W,
        )
        self.directions = (
            self.N,
            self.S,
            self.E,
            self.W,
            self.NE,
            self.NW,
            self.SE,
            self.SW,
        )

        # map size
        max_x = max(x for x, y in self.game_map.keys())
        max_y = max(y for x, y in self.game_map.keys())
        self.map_size = max_x, max_y
        self.map_center = max_x / 2, max_y / 2

        # get the position of our HQ, only if it's unknown
        if not getattr(self, 'own_hq_at', None):
            # this shouldn't fail on the first turn...
            self.own_hq_at = [position
                              for position, tile in self.game_map.items()
                              if tile.own_hq][0]

        # get the position of the enemy HQ, only if it's unknown
        if not getattr(self, 'enemy_hq_at', None):
            try:
                self.enemy_hq_at = [position
                                    for position, tile in self.game_map.items()
                                    if tile.enemy_hq][0]
            except IndexError:
                self.enemy_hq_at = None

        # get a dict of positions and enemies on those positions, just for
        # positions which do have enemies
        self.enemies = dict((position, tile.enemies_count)
                            for position, tile in self.game_map.items()
                            if tile.enemies_count > 0)

        # tactical situation of enemies
        self.invader = closest_to(self.enemies.keys(), self.own_hq_at)

        # get the list of our units
        self.army = []
        for position, tile in self.game_map.items():
            self.army.extend(tile.units)

        # tactical situation of or units
        self.commander = closest_to(self.army, self.own_hq_at)
        if self.enemy_hq_at:
            self.explorer = closest_to(self.army, self.enemy_hq_at)
        else:
            self.explorer = farthest_to(self.army, self.own_hq_at)

        # update data of known unreachable positions
        if not getattr(self, 'known_unreachables', None):
            self.known_unreachables = set()
        for position, tile in self.game_map.items():
            if not tile.reachable:
                self.known_unreachables.add(position)

    def reachable(self, position, is_commander=False):
        """
        Is a tile reachable?
        """
        tile = self.game_map[position]
        return (
            # tile says is reachable
            tile.reachable and
            # is not own HQ, or we are the commander so we can go through it
            (is_commander or not tile.own_hq) and
            # has no enemies
            not tile.enemies_count and
            # was not recorded as unreachable in the past
            (position not in self.known_unreachables)
        )

    def pathfind(self, initial, target, smart=True, is_commander=False):
        """
        Pathfinding from the initial to the target, through valid tiles.
        Returns the best direction to move to.
        """
        initial = as_point(initial)
        target = as_point(target)

        if initial == target:
            # no pathfinding needed
            return None

        if smart:
            method = self.smart_pathfind
        else:
            method = self.dummy_pathfind

        return method(initial, target, is_commander)

    def dummy_pathfind(self, initial, target, is_commander=False):
        """
        Dummy pathfinding from the initial to the target, through valid tiles.
        Returns the best direction to move to.
        """
        moves = self.possible_moves(initial, is_commander)

        if moves:
            # return the direction of the move which brings you closer to the
            # target
            def resulting_distance(move):
                direction, new_position = move
                return distance(new_position, target)

            return list(sorted(moves, key=resulting_distance))[0][0]
        else:
            return None

    def smart_pathfind(self, initial, target, is_commander=False):
        """
        Find a path from the initial to the target, through valid tiles, and
        return the first direction we must follow to reach it.
        """
        def add_new_node(position, direction, cost, parent):
            """
            Create a new node on the fringe, inserted f-ordered.
            """
            node = {
                'position': position,
                'direction': direction,
                'parent': parent,
                'cost': cost,
                'f': cost + distance(position, target)
            }

            i = 0
            while i < len(fringe) and fringe[i]['f'] > node['f']:
                i += 1

            if i == len(fringe):
                # reached end without finding a good position
                fringe.append(node)
            else:
                # found a good position
                fringe.insert(i, node)

        # a-star graph search
        fringe = []
        explored = set()

        add_new_node(position=initial,
                     direction=None,
                     cost=0,
                     parent=None)

        while fringe:
            current = fringe.pop()
            position = current['position']

            if position == target:
                # goal found, get the first direction
                path_node = current
                previous_direction = None
                while path_node['parent']:
                    previous_direction = path_node['direction']
                    path_node = path_node['parent']
                return previous_direction
            else:
                # add reachable positions to the fringe
                moves = self.possible_moves(position, is_commander)

                for direction, new_position in moves:
                    if new_position not in explored:
                        explored.add(new_position)
                        add_new_node(position=new_position,
                                     direction=direction,
                                     cost=current['cost'] + 1,
                                     parent=current)

        # no path found
        return None

    def possible_moves(self, position, is_commander=False):
        """
        Get the valid moves from one position, as tuples with the form
        (direction, new_position).
        """
        x, y = as_point(position)
        # theoretical possible moves
        moves = [(direction, (x + direction.x, y + direction.y))
                 for direction in self.directions]
        # filter out invalid moves
        moves = [(direction, new_position)
                 for direction, new_position in moves
                 if new_position in self.game_map and
                 self.reachable(new_position, is_commander)]

        return moves

    def attack_direction(self, unit, target):
        """
        Calculate the direction needed for an attack. Assumes the target is in
        range.
        """
        xu, yu = as_point(unit)
        target = as_point(target)

        for direction in self.adyacent_directions:
            new_position = (xu + direction.x, yu + direction.y)
            if new_position == target:
                return direction
        # no direction found
        return None

    def commander_at_hq(self):
        """
        Is our commander defending our HQ from the inside?
        """
        return (
            self.commander and
            as_point(self.commander) == self.own_hq_at
        )

    def explorer_can_capture(self):
        """
        Are we able to capture the enmy HQ?
        """
        return (
            # we see the enemy HQ
            self.enemy_hq_at and
            # it's empty
            self.enemy_hq_at not in self.enemies and
            # and we have an explorer
            self.explorer and
            # able to conquer it
            can_move(self.explorer, self.enemy_hq_at)
        )

    def invader_arrived(self):
        """
        Is the enemy at the doors of our HQ?
        """
        return (
            # they have an invader
            self.invader and
            # able to conquer our HQ
            distance(self.invader, self.own_hq_at) < MOVE_RANGE
        )

    # Action related methods

    def move_unit(self, unit, target):
        """
        Move an unit in direction to a specified target.
        """
        direction = self.pathfind(unit,
                                  target,
                                  smart=True,
                                  is_commander=unit is self.commander)
        if direction:
            safe_call(self.move, unit, direction)

    def perform_attacks(self, attackers, target, minimum_safety=0):
        """
        Receives a list of (attacker, target) tuples, and performs the attacks
        grouping units at the same tiles.
        If minimum_safety is specified, only attack when the difference in
        armies is equal or greater than that number.
        """
        by_tiles = defaultdict(lambda: 0)
        for attacker in attackers:
            by_tiles[as_point(attacker)] += 1

        for tile_position, attackers_size in by_tiles.items():
            enemy_count = self.enemies[as_point(target)]
            if (attackers_size - enemy_count) >= minimum_safety:
                direction = self.attack_direction(tile_position, target)
                if direction:
                    safe_call(self.attack,
                              self.game_map[tile_position],
                              direction)

    def capture_enemy_hq(self):
        """
        Moves the explorer towars (or even into) the enmy HQ. Assumes there is
        an enemy HQ visible.
        """
        self.move_unit(self.explorer, self.enemy_hq_at)

    def retreat_commander(self):
        """
        Move the commander to our own HQ. Assumes we have a commander.
        """
        self.move_unit(self.commander, self.own_hq_at)

    def attack_invader(self):
        """
        Attack the invader with every unit we can, except for the commander.
        """
        attackers = []
        for unit in self.army:
            if unit is not self.commander and can_attack(unit, self.invader):
                attackers.append(unit)
            else:
                self.move_unit(unit, self.invader)

        self.perform_attacks(attackers, self.invader)

    def block_invader(self):
        """
        Move defenders to strategic positions which help to intercept invaders.
        The best position is one which minimizes distance between
        (unit, invader) and (unit, own hq) at the same time.
        """
        for unit in self.army:
            if unit is not self.commander:
                if distance(unit, self.own_hq_at) > DEFENSE_DISTANCE:
                    # unit outside defense range, make it come back home
                    # (can't go directly to hq, because it's not the commander)
                    hq_adyacents = [new_position
                                    for direction, new_position
                                    in self.possible_moves(self.own_hq_at)]
                    self.move_unit(unit, closest_to(hq_adyacents,
                                                    self.own_hq_at))
                else:
                    # if the unit is in defense range, try to block the enemy

                    # reachable positions
                    moves = self.possible_moves(unit)
                    # include current position, we want to consider standing
                    # still
                    moves.append((None, as_point(unit)))

                    # don't allow it to go outside the defense range
                    moves = [(direction, new_position)
                             for direction, new_position in moves
                             if distance(new_position,
                                         self.own_hq_at) <= DEFENSE_DISTANCE]

                    if moves:
                        priority_invader = 1
                        priority_hq = 0.5
                        # pick the one which leaves the unit closer to the
                        # invader and the hq at the same time

                        def both_distances(move):
                            direction, new_position = move
                            d_to_invader = distance(new_position, self.invader)
                            d_to_hq = distance(new_position, self.own_hq_at)
                            return (
                                d_to_invader * priority_invader +
                                d_to_hq * priority_hq
                            )

                        best_move = list(sorted(moves, key=both_distances))[0]
                        best_direction, best_new_position = best_move

                        self.move_unit(unit, best_new_position)

    def regroup_defense(self):
        """
        Move defenders to idle positions: adyacent to base minimizing distance
        to center of the map.
        """
        hq_surroundings = [position
                           for direction, position in
                           self.possible_moves(self.own_hq_at)]
        idle_position = closest_to(hq_surroundings, self.map_center)
        for unit in self.army:
            if unit is not self.commander and unit is not self.explorer:
                self.move_unit(unit, idle_position)

    def explore(self):
        """
        Use one unit to explore the map and try to find the enemy HQ. Explore
        center and corners first.
        """
        if not getattr(self, 'to_explore', None):
            # only once, create a set of positions we want to explore
            self.to_explore = set((x, y)
                                  for x in range(self.map_size[0])
                                  for y in range(self.map_size[1])
                                  if (x, y) != self.own_hq_at)

        # remove positions already explored by units
        for unit in self.army:
            position = as_point(unit)
            if position in self.to_explore:
                self.to_explore.remove(position)

        # remove unreachable positions
        for position, tile in self.game_map.items():
            if not tile.reachable and position in self.to_explore:
                self.to_explore.remove(position)

        # center and corners are priority when exploring
        max_x, max_y = self.map_size
        strategic_explore = (
            self.map_center,
            (0, 0),
            (0, max_y - 1),
            (max_x - 1, 0),
            (max_x - 1, max_y - 1),
        )
        # which ones have not been explored?
        strategic_explore = [position for position in strategic_explore
                             if position in self.to_explore]

        if strategic_explore:
            # most probable enemy HQ area
            explore_to = farthest_to(strategic_explore, self.own_hq_at)
        else:
            # just explore area near the explorer
            explore_to = closest_to(self.to_explore, self.explorer)

        if explore_to:
            self.move_unit(self.explorer, explore_to)
