import sys
import os
import time
import dataclasses
import math
import csv
import collections
import traceback
import re
import random
from typing import Dict, Set, Tuple
from pprint import pprint
from selenium.webdriver import Chrome
from selenium.common.exceptions import WebDriverException
import networkx as nx
import matplotlib.pyplot as plt

DB_FNAME = 'friends.csv'
# email \n password
CREDENTIALS_FNAME = 'credentials.txt'


def main(argv) -> int:
    if len(argv) != 2:
        print_help(argv[0])
        return 1

    if argv[1] == 'init':
        Facebook.init_db()
    elif argv[1] == 'collect':
        Facebook.collect()
    elif argv[1] == 'all':
        Facebook.init_collect()
        friends = read_friends()
        interpret(friends)
    elif argv[1] == 'interpret':
        friends = read_friends()
        interpret(friends)
    elif argv[1] in ('--help', '-h'):
        print_help(argv[0])
    else:
        print_help(argv[0])
        return 1

    return 0


def print_help(program):
    print(f'usage: {program} (collect|interpret|init|all)')


class Facebook(Chrome):
    BASE_URL = 'https://m.facebook.com'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.friends: Dict[str, Tuple[str, List[str]]] = {}
        # a stack with sentinel value
        self.todo_names: List[name] = [None]
        self.touch_db_file()
        self.read_db()

    @classmethod
    def init_db(cls):
        with cls() as self:
            self._init_db()

    @classmethod
    def collect(cls):
        with cls() as self:
            self.get_mutuals()

    @classmethod
    def init_collect(cls):
        with cls() as self:
            self._init_db()
            self.get_mutuals()

    def __enter__(self):
        super().__enter__()
        self.login(*self.read_credentials())
        return self

    @staticmethod
    def read_credentials():
        with open(CREDENTIALS_FNAME) as f:
            return f.read().splitlines()

    def login(self, email, password):
        self.get(self.BASE_URL)
        email_field = self.find_element_by_id('m_login_email')
        password_field = self.find_element_by_id('m_login_password')
        email_field.send_keys(email)
        password_field.send_keys(password)
        login_form = self.find_element_by_id('login_form')
        login_form.submit()

    def get_mutuals(self):
        while (name := self.todo_names.pop()) is not None:
            try:
                self.get_friend_mutuals(name)
            except (WebDriverException, ValueError) as e:
                traceback.print_tb(e.__traceback__)
                print(f'{type(e).__name__}: {e}')
                break
            else:
                time.sleep(random.randrange(30, 90))

        self.commit_db()

    def get_friend_mutuals(self, name):
        print(f'trying {name}')
        url = self.friends[name][0]

        if re.match(r'https://m\.facebook\.com/profile\.php\?id=\d*', url):
            url += '&v=friends&mutual=1'
        else:
            url += '/friends?mutual=1'

        self.get(url)
        self.scroll_all_the_way_down()
        elements = self.find_elements_by_class_name('_52jh')

        if not elements:
            raise ValueError('webpage empty')
            return

        mutuals = self.friends[name][1]

        for element in elements:
            link = element.find_element_by_tag_name('a')
            friend_name = link.text
            url = link.get_attribute('href')
            self.add_new_friend(friend_name, url)
            mutuals.append(friend_name)

        print(f'{name}: {mutuals}')

    def _init_db(self):
        os.remove(DB_FNAME)
        self.touch_db_file()
        self.read_db()
        self.get_my_friends()
        self.commit_db()

    def touch_db_file(self):
        if not os.path.exists(DB_FNAME):
            with open(DB_FNAME, 'x') as f:
                pass

    def get_my_friends(self):
        self.get(self.BASE_URL + '/friends/center/friends')
        self.scroll_all_the_way_down()
        elements = self.find_elements_by_class_name('_52jh')

        for element in elements:
            link = element.find_element_by_tag_name('a')
            name = link.text
            url = link.get_attribute('href')
            self.add_new_friend(name, url)

    def add_new_friend(self, name, url):
        if name not in self.friends:
            self.friends[name] = url, []
            self.todo_names.append(name)

    def commit_db(self):
        with open(DB_FNAME, 'w') as f:
            writer = csv.writer(f)
            friends = sorted(self.friends.items(), key=sort_key)

            for name, (url, mutuals) in friends:
                mutuals = sorted(mutuals, key=sort_key)
                writer.writerow([name, url, *mutuals])

        self.read_db()

    def read_db(self):
        self.friends = read_db_helper()
        self.todo_names = [None]

        for name, (url, mutuals) in self.friends.items():
            if not mutuals:
                self.todo_names.append(name)

    def scroll_all_the_way_down(self, pause_time=1):
        current_height = self.height()
        i = 0

        while True:
            self.execute_script(f'window.scrollTo(0, {current_height});')

            if pause_time:
                time.sleep(pause_time)
            else:
                return

            if (new_height := self.height()) != current_height:
                current_height = new_height
            else:
                return i

            i += 1

    def height(self):
        return self.execute_script('return document.body.scrollHeight')


def read_friends():
    friends = {}

    for name1, (url, mutuals) in read_db_helper().items():
        mutuals1 = friends_emplace(friends, name1)

        if mutuals == ['Null']:
            continue

        for name2 in mutuals:
            mutuals2 = friends_emplace(friends, name2)
            # direct graph
            mutuals1.add(name2)
            mutuals2.add(name1)

    return friends


def friends_emplace(friends, name):
    if name not in friends:
        friends[name] = set()

    return friends[name]


def read_db_helper():
    friends = {}

    with open(DB_FNAME) as f:
        for name, url, *mutuals in csv.reader(f):
            friends[name] = url, mutuals

    return friends


def interpret(friends):
    plot_edges(iter_edges(friends), 'graph.png')
    plot_edges(iter_kruskals(friends), 'mst.png')
    score = hub_score(friends)
    plot_edges(
        ((name1, name2, max(score[name1], score[name2]))
         for name1, name2, _ in iter_kruskals(friends)),
        'mst2.png')

    with open('hub-score.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(sorted(score.items(),
                                key=lambda i: i[1], reverse=True))

    with open('friends.txt', 'w') as f:
        print_friends(friends, file=f)


def plot_edges(edges, fname):
    fig, ax = plt.subplots(figsize=(16, 9))
    G = nx.Graph()

    for name1, name2, weight in edges:
        G.add_edge(name1, name2, weight=weight)

    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=10, ax=ax)
    nx.draw_networkx_edges(G, pos, width=1, alpha=0.5, edge_color='b', ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif',
                            ax=ax)

    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(fname)
    plt.axis('off')
    plt.show()


def iter_kruskals(friends):
    names = list(friends)
    edges = sorted(iter_edges(friends), key=lambda t: t[2], reverse=True)
    reps = list(range(len(names)))

    for name1, name2, weight in edges:
        i = names.index(name1)
        j = names.index(name2)
        rep1 = union_find(reps, i)
        rep2 = union_find(reps, j)

        if rep1 == rep2:
            continue

        reps[rep1] = rep2
        yield name1, name2, weight


def union_find(reps, x):
    if reps[x] != x:
        reps[x] = union_find(reps, reps[x])

    return reps[x]


def iter_edges(friends):
    for name1, mutuals1 in friends.items():
        for name2 in mutuals1:
            # undo the direct-ness of the graph
            if name2 < name1:
                continue

            if name2 in mutuals1:
                mutuals2 = friends[name2]
                weight = len(mutuals1.intersection(mutuals2))
                weight = float(weight + 1)
                yield name1, name2, weight


def hub_score(friends):
    score = collections.defaultdict(int)

    for name1, name2, weight in iter_kruskals(friends):
        score[name1] += 1
        score[name2] += 1

    return score


def print_friends(friends, file):
    print('{', file=file)

    for name, mutuals in sorted(friends.items(), key=sort_key):
        mutuals = sorted(mutuals, key=sort_key)
        print(f'\t{name!r}: {mutuals!r},', file=file)

    print('}', file=file)


def sort_key(name_or_items):
    if isinstance(name_or_items, str):
        name = name_or_items
    elif isinstance(name_or_items, tuple):
        name = name_or_items[0]

    *names, last = name.split()
    return last, *names


if __name__ == '__main__':
    returncode = main(sys.argv)

    if returncode:
        sys.exit(returncode)
