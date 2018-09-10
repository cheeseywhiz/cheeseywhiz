import dataclasses
import enum
import functools
import multiprocessing
import pprint
import random
import time
from matplotlib import pyplot as plt
import numpy as np

N_CONTROL = 40
N_CONTROL_SWIM = 14
N_TEST = 84
N_TEST_SWIM = 0

SAMPLE_SIZE = 20
N_SAMPLES = 1_000_000


def timeit(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        t_0 = time.perf_counter()
        value = func(*args, **kwargs)
        t_1 = time.perf_counter()
        print(f'{func.__name__} execution time {t_1 - t_0} seconds')
        return value

    return wrapped


Treatment = enum.Enum('Treatment', 'control test')


@dataclasses.dataclass
class SeaMonkey:
    treatment: Treatment
    is_swimming: bool


def do_experiment():
    return [
        *([SeaMonkey(Treatment.control, True)] * N_CONTROL_SWIM),
        *([SeaMonkey(Treatment.control, False)] * (N_CONTROL
                                                   - N_CONTROL_SWIM)),
        *([SeaMonkey(Treatment.test, True)] * N_TEST_SWIM),
        *([SeaMonkey(Treatment.test, False)] * (N_TEST - N_TEST_SWIM)),
    ]


def get_observations(sample):
    control_swim = 0
    control_not_swim = 0
    test_swim = 0
    test_not_swim = 0

    for sea_monkey in sample:
        if sea_monkey.treatment is Treatment.control:
            if sea_monkey.is_swimming:
                control_swim += 1
            else:
                control_not_swim += 1
        elif sea_monkey.treatment is Treatment.test:
            if sea_monkey.is_swimming:
                test_swim += 1
            else:
                test_not_swim += 1

    return np.array([
        [control_swim, control_not_swim],
        [test_swim, test_not_swim],
    ])


def table_sums(table):
    row_sums = [sum(row) for row in table]
    column_sums = [
        sum(row[i] for row in table)
        for i in range(table.shape[1])]
    return row_sums, column_sums, table.sum()


def get_expected(observations):
    row_sums, column_sums, table_sum = table_sums(observations)
    expected = np.empty(observations.shape)

    for i, row in enumerate(observations):
        for j, _ in enumerate(row):
            row_sum = row_sums[i]
            column_sum = column_sums[j]
            expected[i][j] = row_sum * column_sum / table_sum

    return expected


def get_chisq(observations):
    expected = get_expected(observations)
    return (((observations - expected) ** 2) / expected).sum()


def describe(data):
    five_num_sum = np.quantile(data, [0, 1 / 4, 1 / 2, 3 / 4, 1])

    return {
        'minimum': five_num_sum[0],
        '1st quartile': five_num_sum[1],
        'median': five_num_sum[2],
        '3rd quartile': five_num_sum[3],
        'maximum': five_num_sum[4],
        'mean': data.mean(),
        'standard deviation': data.std(),
        'legth': data.size,
    }


@timeit
def get_chisqs(population):
    chisqs = []

    for _ in range(N_SAMPLES):
        sample = random.sample(population, SAMPLE_SIZE)
        observations = get_observations(sample)
        chisq = get_chisq(observations)

        if not np.isnan(chisq):
            chisqs.append(chisq)

    return chisqs


def main():
    population = do_experiment()
    chisqs = get_chisqs(population)
    pprint.pprint(describe(np.array(chisqs)))
    plt.hist(chisqs)
    plt.show()


if __name__ == '__main__':
    main()
