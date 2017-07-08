from random import choice, randint, random
from string import ascii_letters, digits


def wifi_data():
    def rand_pf():
        return {
            'SSID': ''.join(
                choice(ascii_letters + digits) for _ in range(randint(8, 32))),
            'connected': False,
            'secure': (False, True)[random() < (2 / 3)],
            'signal': randint(25, 99),
        }

    def sort_key(pf):
        return pf['signal']

    res = sorted([rand_pf() for _ in range(randint(3, 30))], key=sort_key)
    pf = choice(res[:3])
    pf['connected'] = True
    pf['secure'] = True
    return res


def main():
    # for use with interactive shell
    global data
    data = wifi_data()
    print(data)


if __name__ == '__main__':
    main()