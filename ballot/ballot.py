#!/usr/bin/python
# coding=utf-8
import os
import sys
from datetime import datetime


def read_results(path):
    results = {}
    with open(path) as backup:
        for line in backup.read().split('\n'):
            if line.strip():
                candidate, votes = line.split(':')
                results[candidate] = int(votes)
    return results


def save_results(path, results):
    with open(path, 'w') as backup:
        for candidate, votes in results.items():
            backup.write('%s:%i\n' % (candidate.replace(':', ''), votes))


def vote(initial_data=None):
    results = {}

    if initial_data:
        results.update(initial_data)

    backup_path = 'results_%s.txt' % datetime.now().strftime('%Y%m%d_%H%M%S')

    while True:
        os.system('clear')
        output = u'\n Voting:\n ' + '_' * 60 + '\n\n'
        for candidate, votes in reversed(sorted(results.items(), key=lambda p: p[1])):
            bar = u'·' * votes
            output += u' %s %s (%i)\n' % (bar, candidate, votes)

        output = output.encode('utf-8')
        print output

        save_results(backup_path, results)

        try:
            candidate = raw_input(' Vote for: ')
        except KeyboardInterrupt:
            break

        if candidate:
            candidate = candidate.title()
            adds = not candidate.startswith('-')
            candidate = candidate.replace('-', '')
            results[candidate] = results.get(candidate, 0) + (1 if adds else -1)
            if results[candidate] < 1:
                del results[candidate]


if __name__ == '__main__':
    if len(sys.argv) > 1:
        initial_data = read_results(sys.argv[1])
    else:
        initial_data = None

    vote(initial_data)
