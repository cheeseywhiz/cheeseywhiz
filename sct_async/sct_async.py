#!/usr/bin/env python3
from dataclasses import dataclass
import functools
from pprint import pprint as pp
import random
import sys
import time
import types


@dataclass
class Return:
    value: object


@dataclass
class Sleep:
    pass


def get_log(task, mute=False):
    def log(*args, **kwargs):
        if mute:
            return
        print(task, ':', sep='', end='')
        print(*args, **kwargs)

    def intervene(message, x_message=None):
        log('INTERVENE:')

        if x_message is not None:
            log(message, '? x = ', x_message, sep='')
        else:
            log(message, '?', sep='')

        x = None
        breakpoint() # do not remove
        #log(x) # debugging
        return x

    log.intervene = intervene
    return log


def i_yield():
    yield j_yield()
    return 'i'


def j_yield():
    yield
    return 'j'


def async_sleep(n):
    log = get_log('async_sleep')
    start_time = time.time()
    while True:
        #yield i_yield()
        yield
        if (current_time := time.time()) - start_time >= n:
            return current_time


FIZZBUZZ = []


def produce_fizz_buzz():
    log = get_log('produce_fizz_buzz')

    while True:
        current_time = yield async_sleep(random.random())
        current_time = int(current_time)

        if current_time % 15 == 0:
            FIZZBUZZ.append(f'FIZZBUZZ: {current_time}')
        elif current_time % 5 == 0:
            FIZZBUZZ.append(f'BUZZ: {current_time}')
        elif current_time % 3 == 0:
            FIZZBUZZ.append(f'FIZZ: {current_time}')


def print_fizz_buzz():
    log = get_log('print_fizz_buzz')

    while True:
        current_time = yield async_sleep(3)

        while FIZZBUZZ:
            log(FIZZBUZZ.pop(0))


def runtime(*threads):
    log = get_log('runtime', mute=True)
    tasks = [([], thread(), None) for thread in threads]
    i = 0

    while tasks:
        #pp(tasks)
        senders, task, returnValue = tasks.pop(0)

        try:
            future = task.send(returnValue)

            if isinstance(future, types.GeneratorType):
                log('yielded a task')
                tasks.append(([*senders, task], future, None))
            elif future is None:
                log('task yielded its time')
                tasks.append((senders, task, None))
            else:
                log.intervene('bad future')
                return
        except StopIteration as returnValue:
            log(f'task returned {returnValue.value=}')
            if senders:
                *senders, sender = senders
                tasks.append((senders, sender, returnValue.value))

        i += 1
        #breakpoint()

    log(f'{i=}')


if __name__ == '__main__':
    runtime(print_fizz_buzz, produce_fizz_buzz)
