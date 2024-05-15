#!/usr/bin/env python3
from dataclasses import dataclass
import functools
import pprint
import random
import sys
import time
import types

DEBUG_RUNTIME = True


def get_log(task, mute=False):
    def log(*args, **kwargs):
        if mute:
            return
        print(int(time.time()), ':', task, ':', sep='', end='')
        print(*args, **kwargs)

    def pp(*args, msg='', **kwargs):
        if mute:
            return
        log('\n'.join([msg, pprint.pformat(*args, **kwargs)]))

    log.pp = pp

    def intervene(message, x_message=None):
        if mute:
            return
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


FIZZBUZZ = []


def produce_fizz_buzz():
    global FIZZBUZZ
    log = get_log('produce_fizz_buzz', mute=True)
    last_time = None
    skipped = False
    i = 0

    while i < 20:
        expected_value = (1 + 0.5) / 2

        if skipped:
            sleep_time = 1 - expected_value
        else:
            sleep_time = (1 + random.random()) / 2

        skipped = False
        current_time = yield async_sleep(sleep_time)
        current_time = int(current_time)

        if current_time == last_time:
            skipped = True
            continue

        last_time = current_time

        if current_time % 15 == 0:
            FIZZBUZZ.append(f'FIZZBUZZ: {current_time}')
            log('FIZZBUZZ')
            i += 1
        elif current_time % 5 == 0:
            FIZZBUZZ.append(f'BUZZ: {current_time}')
            log('BUZZ')
            i += 1
        elif current_time % 3 == 0:
            FIZZBUZZ.append(f'FIZZ: {current_time}')
            log('FIZZ')
            i += 1


def print_fizz_buzz():
    global FIZZBUZZ
    log = get_log('print_fizz_buzz')
    i = 0

    while i < 20:
        while FIZZBUZZ:
            log(FIZZBUZZ.pop(0))
            i += 1
        yield async_sleep(3)


def async_sleep(n):
    log = get_log('async_sleep')
    yield LibraryEvent.Sleep(n)
    return time.time()


class LibraryEvent:
    @dataclass
    class Sleep:
        amount: float


class RuntimeEvent:
    @dataclass
    class Return:
        value: object

    @dataclass
    class WakeTime:
        wake_time: float

        def is_ready(self):
            return time.time() >= self.wake_time


def runtime(*threads):
    log = get_log('runtime', mute=not DEBUG_RUNTIME)
    tasks = [([], thread(), None) for thread in threads]
    i = 0

    while tasks:
        analyze_tasks(tasks)
        senders, task, runtimeEvent = tasks.pop(0)
        log(f'will run {task}')

        try:
            if isinstance(runtimeEvent, RuntimeEvent.Return):
                future = task.send(runtimeEvent.value)
            else:
                future = next(task)

            if isinstance(future, types.GeneratorType):
                log('yielded a task')
                tasks.append(([*senders, task], future, None))
            elif future is None:
                log('task yielded its time')
                sleep_amount = 0.1
                wake_time = time.time() + sleep_amount
                tasks.append((senders, task, RuntimeEvent.WakeTime(wake_time)))
            elif isinstance(future, LibraryEvent.Sleep):
                log(f'task will sleep for {future.amount} s')
                wake_time = time.time() + future.amount
                tasks.append((senders, task, RuntimeEvent.WakeTime(wake_time)))
            else:
                log.intervene('bad future')
                return
        except StopIteration as returnValue:
            log(f'task returned {returnValue.value=}')
            if senders:
                *senders, sender = senders
                tasks.append((senders, sender, RuntimeEvent.Return(returnValue.value)))

        i += 1
        #breakpoint()

    log(f'{i=}')


def analyze_tasks(tasks):
    log = get_log('analyze_tasks', mute=not DEBUG_RUNTIME)
    log.pp(tasks)

    # sleep until the next task is ready
    if all(isinstance(runtimeEvent, RuntimeEvent.WakeTime) for _, _, runtimeEvent in tasks):
        # sort by wake up time
        tasks.sort(key=lambda runtimeEvent: runtimeEvent[2].wake_time)
        earliest_time = tasks[0][2].wake_time
        diff = earliest_time - time.time()
        log(f'sleeping for {diff} s\n')
        if diff > 0: time.sleep(diff)

    # we can do this because now there should be at least one event that is ready
    while isinstance(tasks[0][2], RuntimeEvent.WakeTime) and not tasks[0][2].is_ready():
        tasks.append(tasks.pop(0))

    log.pp(tasks[0], msg='will run:')


if __name__ == '__main__':
    runtime(print_fizz_buzz, produce_fizz_buzz)
