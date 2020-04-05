import sys
import os
import time
import dataclasses
import math
import csv
import collections
import traceback
import re
from typing import Dict, Set
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
        return 0
    elif argv[1] == 'collect':
        Facebook.collect()
        return 0
    elif argv[1] == 'interpret':
        friends = read_friends()
        interpret(friends)
        return 0
    elif argv[1] in ('--help', '-h'):
        print_help(argv[0])
        return 0

    print_help(argv[0])
    return 1



def print_help(program):
    print(f'usage: {program} (collect|interpret|init)')


class Facebook(Chrome):
    BASE_URL = 'https://m.facebook.com'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # a stack w/ sentinel value
        self.todo_names: List[name] = [None]
        # also serves as the set of all names
        self.urls: Dict[str, str] = {}
        # only new rows go in here
        self.mutuals: Dict[str, List[str]] = collections.defaultdict(list)
        self.read_db()

    @classmethod
    def init_db(cls):
        with cls() as self:
            self._init_db()

    @classmethod
    def collect(cls):
        with cls() as self:
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
                time.sleep(20)

        self.commit_db()

    def get_friend_mutuals(self, name):
        print(f'trying {name}')
        url = self.urls[name]

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

        mutuals = self.mutuals[name]

        for element in elements:
            link = element.find_element_by_tag_name('a')
            name = link.text
            url = link.get_attribute('href')
            self.add_new_friend(name, url)
            mutuals.append(name)

        print(f'{name}: {mutuals}')

    def _init_db(self):
        os.remove(DB_FNAME)

        with open(DB_FNAME, 'x') as new_file:
            pass

        self.read_db()
        self.get_my_friends()
        self.commit_db()

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
        if name not in self.urls:
            self.todo_names.append(name)
            self.urls[name] = url
            self.mutuals[name]

    def commit_db(self):
        with open(DB_FNAME, 'a') as f:
            writer = csv.writer(f)

            for name, mutuals in sorted(self.mutuals.items(),
                                        key=lambda i: sort_key(i[0])):
                writer.writerow([name, self.urls[name], *mutuals])

        self.read_db()

    def read_db(self):
        self.todo_names = [None]
        self.urls.clear()
        self.mutuals.clear()

        with open(DB_FNAME) as f:
            for name, url, *mutuals in csv.reader(f):
                self.urls[name] = url

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


def getchar():
    return sys.stdin.read(1)


@dataclasses.dataclass(repr=False, eq=False)
class Friend:
    name: str
    mutuals: Set['Friend'] = dataclasses.field(default_factory=set)

    def sort_key(self):
        return sort_key(self.name)

    def weight(self, friend: 'Friend'):
        if friend in self.mutuals:
            weight = len(self.mutuals.intersection(friend.mutuals))
            weight = float(weight + 1)
        else:
            weight = math.inf

        return weight

    def __repr__(self):
        mutuals = sorted(self.mutuals, key=type(self).sort_key)
        mutuals = [friend.name for friend in mutuals]

        if mutuals:
            cls = type(self).__qualname__
            return f'{cls}(name={self.name!r}, mutuals={mutuals!r})'
        else:
            return repr(self.name)

    def __str__(self):
        if self.mutuals:
            return repr(self)
        else:
            return self.name


def sort_key(name):
    *names, last = name.split()
    return last, *names


class Friends(collections.abc.Set):
    def __init__(self):
        self.friends = {}

    def emplace(self, name):
        if name in self.friends:
            friend = self.friends[name]
        else:
            friend = Friend(name)
            self.friends[name] = friend

        return friend

    def __contains__(self, friend):
        return friend.name in self.friends

    def __iter__(self):
        return iter(self.friends.values())

    def __len__(self):
        return len(self.friends)


def read_friends() -> Friends:
    with open(DB_FNAME) as f:
        reader = csv.reader(f)
        data = list(reader)

    friends = Friends()

    for name1, url, *mutuals in data:
        friend1 = friends.emplace(name1)

        for name2 in mutuals:
            friend2 = friends.emplace(name2)
            # make direct graph
            friend1.mutuals.add(friend2)
            friend2.mutuals.add(friend1)

    return friends


def interpret(friends: Friends):
    plot_edges(iter_edges(friends), 'graph.png')
    plot_edges(iter_kruskals(friends), 'mst.png')

    with open('hub-score.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(sorted(hub_score(friends).items(),
                                key=lambda i: i[1], reverse=True))

    with open('friends.txt', 'w') as f:
        print_friends(friends, f)


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


def iter_kruskals(friends: Friends):
    names = [friend.name for friend in friends]
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


def iter_edges(friends: Friends):
    for friend1 in friends:
        name1 = friend1.name

        for friend2 in friend1.mutuals:
            name2 = friend2.name

            # undo the direct-ness of the graph
            if name2 < name1:
                continue

            if (weight := friend1.weight(friend2)) != math.inf:
                yield name1, name2, weight


def hub_score(friends: Friends):
    score = collections.defaultdict(int)

    for name1, name2, weight in iter_kruskals(friends):
        score[name1] += 1
        score[name2] += 1

    return score


def print_friends(friends: Friends, file):
    print('{\t', file=file)

    for friend in sorted(friends, key=Friend.sort_key):
        print(f'\t{friend!r},', file=file)

    print('}', file=file)


if __name__ == '__main__':
    returncode = main(sys.argv)

    if returncode:
        sys.exit(returncode)
