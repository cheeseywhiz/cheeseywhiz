import builtins
import math

PHI = (1 + math.sqrt(5)) / 2
PI = math.pi


def reversed(an_iter):
    return builtins.reversed(list(an_iter))


def repeat(an_object):
    while True:
        yield an_object


def trunc_cont(numbers: list):
    srebmun = reversed(numbers)
    frac = next(srebmun)

    for n in srebmun:
        frac = n + 1 / frac

    return frac


def cont_terms(number: float):
    while True:
        integer = int(number)
        yield integer
        decimal = number - integer

        if not decimal:
            return

        number = 1 / decimal


def trunc_cont_terms(number: float, n_terms: int):
    return [n for i, n in zip(range(n_terms), cont_terms(number))]


def trunc_cont_terms_limit(number: float, limit: int=200):
    terms = []

    for term in cont_terms(number):
        if term < limit:
            terms.append(term)
        else:
            break

    return terms


def terms_to_frac(terms: list):
    srebmun = reversed(terms)
    num = 1
    den = next(srebmun)

    for a in srebmun:
        num = a * den + num
        num, den = den, num

    return den, num


def num_to_frac(number: float):
    return terms_to_frac(trunc_cont_terms(number, 100))
