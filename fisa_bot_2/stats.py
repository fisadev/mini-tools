#!/usr/bin/env python
# coding: utf-8
import json
from collections import namedtuple
from operator import itemgetter
from os.path import exists
from time import sleep

from matplotlib import pyplot
from pyquery import PyQuery
from requests import session


BASE_URL = 'https://pytron.onapsis.com/'
LOGIN_URL = BASE_URL + 'accounts/login/'
MATCH_URL = BASE_URL + 'get-match/%i'
MEMORY_PATH = 'memory.json'

USER_CHANGES = {
    'lcubo': 'ONA.lcubo',
    'max': 'ONA.max',
    'locosuelto': 'ONA.locosuelto',
    'samo': 'ONA.samo',
    'emi': 'ONA.emi',
    'Thundercats': 'ONA.Thundercats',
}


Match = namedtuple('Match', ('result_kind',
                             'player1',
                             'player2',
                             'time',
                             'moves'))


class MatchesCrawler(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.session = session()
        self.session.headers.update({'Referer': 'https://pytron.onapsis.com/',
                                     'Origin': 'https://pytron.onapsis.com',
                                     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.114 Safari/537.36'})

    def browse(self, url, post=False, data={}):
        if post:
            method = self.session.post
        else:
            method = self.session.get

        r = method(url, data=data, verify=False)
        return r

    def get_xsrf_token(self, response):
        pq = PyQuery(response)
        return pq('input[name=csrfmiddlewaretoken]').val()

    def login(self):
        content = self.browse(BASE_URL).content

        login_data = {
            'username': self.username,
            'password': self.password,
            'csrfmiddlewaretoken': self.get_xsrf_token(content),
            'next': '/',
        }
        sleep(5)

        return self.browse(LOGIN_URL, post=True, data=login_data)

    def final_player(self, player):
        return USER_CHANGES.get(player, player)

    def get_match(self, match_id):
        r = self.browse(MATCH_URL % match_id)

        if r.status_code == 200:
            info = json.loads(r.content)
            result = info['result']
            time = float(info['elapsed']) * 1000
            moves = len(info['moves'])
            if len(result['lost'].keys()) == 2:
                kind = 'Tie'
                player1, player2 = map(self.final_player, info['players'])
            else:
                kind = 'Win'
                player1 = self.final_player(result['winner'])
                player2 = self.final_player(result['lost'].keys()[0])

            return Match(kind,
                         player1,
                         player2,
                         time,
                         moves)
        else:
            return None

    def get_matches(self, infinite=False):
        print 'Login...'
        self.login()

        matches = MatchesCrawler.load()

        i = 1
        keep_looking = True
        while keep_looking:
            print 'Match', i

            if i in matches:
                print 'Known match'
                i += 1
            else:
                print 'Getting info...'
                try:
                    result = self.get_match(i)
                    if result:
                        print result
                        matches[i] = result
                        MatchesCrawler.save(matches)
                        sleep(3)
                        i += 1
                    else:
                        print 'Not found'
                        if infinite:
                            sleep(30)
                        else:
                            return matches
                except Exception as err:
                    print 'ERROR', err.message
                    sleep(60)

    @classmethod
    def load(cls):
        if exists(MEMORY_PATH):
            with open(MEMORY_PATH) as memory_file:
                data_as_dicts = json.load(memory_file)

            return dict((int(i), Match(**match))
                        for i, match in data_as_dicts.items())
        else:
            return {}

    @classmethod
    def save(cls, matches):
        with open(MEMORY_PATH, 'w') as memory_file:
            data_as_dicts = dict((i, match.__dict__) for i, match in sorted(matches.items()))
            json.dump(data_as_dicts, memory_file, indent=1)


class Stats(object):
    def __init__(self, matches):
        self.calculate_stats(matches)

    def get_players(self, matches):
        players = set()

        for match in matches.values():
            players.add(match.player1)
            players.add(match.player2)

        return list(players)

    def calculate_stats(self, matches):
        self.players = self.get_players(matches)

        self.wins_count = dict((player, 0) for player in self.players)
        self.ties_count = dict((player, 0) for player in self.players)
        self.loses_count = dict((player, 0) for player in self.players)

        self.wins_lines = dict((player, {0: 0}) for player in self.players)

        self.wins_vs_loses_lines = dict((player, {0: 0}) for player in self.players)
        self.wins_vs_loses_count = dict((player, 0) for player in self.players)

        self.wins_percent = dict((player, 0) for player in self.players)

        self.matches_lines = dict((player, {0: 0}) for player in self.players)
        self.matches_count = dict((player, 0) for player in self.players)

        enemies = dict((player, dict((player2, 0) for player2 in self.players))
                       for player in self.players)

        self.times_line = {}
        self.moves_line = {}
        self.moves_per_hour_line = {}

        for i, match in sorted(matches.items()):
            if match.result_kind == 'Win':
                self.wins_count[match.player1] += 1
                self.loses_count[match.player2] += 1

                self.wins_vs_loses_count[match.player1] += 1
                self.wins_vs_loses_count[match.player2] -= 1

                enemies[match.player2][match.player1] += 1
            else:
                self.ties_count[match.player1] += 1
                self.ties_count[match.player2] += 1

            self.matches_count[match.player1] += 1
            self.matches_count[match.player2] += 1

            for player in self.players:
                self.wins_lines[player][i] = self.wins_count[player]
                self.wins_vs_loses_lines[player][i] = self.wins_vs_loses_count[player]
                self.matches_lines[player][i] = self.matches_count[player]

            self.times_line[i] = match.time
            self.moves_line[i] = match.moves
            self.moves_per_hour_line[i] = (3600.0 / match.time) * match.moves

        for player in self.players:
            self.wins_percent[player] = self.wins_count[player] * (100.0 / self.matches_count[player])

        self.worst_enemies = {}
        for player in self.players:
            max_losts = max(enemies[player].values())
            self.worst_enemies[player] = [player2 for player2, losts in enemies[player].items()
                                          if losts == max_losts]

    def graph_times(self):
        self._draw_lines({'time': self.times_line})

    def graph_moves(self):
        self._draw_lines({'moves': self.moves_line})

    def graph_moves_per_hour(self):
        self._draw_lines({'moves per hour': self.moves_per_hour_line})

    def graph_wins_lines(self):
        self._draw_lines(self.wins_lines)

    def graph_wins_vs_loses_lines(self):
        self._draw_lines(self.wins_vs_loses_lines)

    def graph_matches_lines(self):
        self._draw_lines(self.matches_lines)

    def graph_player_results(self):
        self._draw_bars([('wins', 'g', self.wins_count),
                         ('ties', 'y', self.ties_count),
                         ('loses', 'r', self.loses_count)])

    def graph_win_percents(self):
        self._draw_bars([('win percent', 'g', self.wins_percent)])

    def _draw_lines(self, lines):
        max_i = max(lines.values()[0].keys())

        for player, line in lines.items():
            steps, values = zip(*sorted(line.items()))
            pyplot.plot(steps, values, label=player)
            pyplot.text(max_i * 1.01, values[max_i - 1],
                        '%s (%i)' % (player, values[max_i - 1]))

        pyplot.show()

    def _draw_bars(self, counts):
        sorted_players = [player for player, value in sorted(counts[0][2].items(), key=itemgetter(1))]
        players_indexes = xrange(len(sorted_players))

        last_values = [0 for player in sorted_players]

        for name, color, sub_counts in counts:
            values = [sub_counts[player] for player in sorted_players]

            pyplot.bar(players_indexes, values, bottom=last_values, color=color, label=name)

            for i, last_value in enumerate(last_values):
                last_values[i] = last_value + values[i]

        pyplot.legend(loc=0)
        pyplot.xticks(players_indexes, sorted_players, rotation=90)
        pyplot.show()


if __name__ == '__main__':
    # this was left running while the people played, to get the lastest matches info
    # mc = MatchesCrawler(raw_input('Username: '), raw_input('Password: '))
    # mc.get_matches(infinite=True)

    # simple usage example:
    m = MatchesCrawler.load()
    s = Stats(m)

    s.graph_player_results()
    s.graph_win_percents()

    s.graph_wins_lines()
    s.graph_wins_vs_loses_lines()

    s.graph_matches_lines()

    s.graph_times()
    s.graph_moves()
    s.graph_moves_per_hour()

