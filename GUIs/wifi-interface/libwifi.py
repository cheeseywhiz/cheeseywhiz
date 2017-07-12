import re
import subprocess
from collections.abc import MutableMapping


def wifi_data():
    def split_keep(self):
        regex = re.compile('BSS ..:')
        matches = regex.findall(self)
        data = regex.split(self)[1:]
        return (
            ''.join(pair)
            for pair in zip(matches, data))

    networks = []
    stdout = subprocess.run(
        'sudo iw dev wlp6s0 scan',
        shell=True, stdout=subprocess.PIPE).stdout
    data = stdout.decode('utf-8')
    data = [
        [chunk.strip()
         for chunk in netw.splitlines()]
        for netw in split_keep(data)]

    for profile_scan in data:
        new_netw = {
            'SSID': '',
            'connected': False,
            'secure': False,
            'signal': 0, }
        for entry in profile_scan:
            if 'SSID' in entry:
                new_netw['SSID'] = re.split(r'SSID: *', entry)[1]
            elif 'associated' in entry:
                new_netw['connected'] = True
            elif 'RSN' in entry:
                new_netw['secure'] = True
            elif 'signal' in entry:
                signal = re.search(r'\d\d', entry).group(0)
                new_netw['signal'] = int(signal)
        networks.append(new_netw)

    def sort_key(netw):
        return netw['signal']

    return sorted(networks, key=sort_key)


def random_data():
    from random import choice, randint, random
    from string import ascii_letters, digits

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
    choice(res[:3])['connected'] = True
    return res


class Profile(MutableMapping):
    # implement abstract methods

    def __getitem__(self, key):
        return self.__dict.__getitem__(key)

    def __setitem__(self, key, value):
        self.__dict.__setitem__(key, value)

    def __delitem__(self, key):
        self.__dict.__delitem__(key)

    def __iter__(self):
        return self.__dict.__iter__()

    def __len__(self):
        return self.__dict.__len__()

    # implement class

    def __init__(self, a_dict, **kwargs):
        self.__dict = a_dict
        self['key'] = ''
        self.pf_name = f"{self['SSID'].split(' ')[0][:8]}-profile"
        self.pf_path = f'/etc/netctl/{self.pf_name}'

    def profile_str(self):
        description, essid, key = (line.replace(' ', '\ ') for line in (
            'Automatically generated by cheese\'s netctl tool',
            self['SSID'],
            self['key']))

        return '\n'.join(filter(None, [
            f'Description={description}',
            'Interface=wlp6s0',
            'Connection=wireless',
            'Security=wpa' if self['secure'] else None,
            f'ESSID={essid}',
            'IP=dhcp',
            f'Key={key}' if self['secure'] else None, ]))

    def generate_profile(self):
        subprocess.run(
            f"sudo echo '{self.profile_str()}' | sudo dd of={self.pf_path}",
            shell=True)

    def command(self, cmd):
        return subprocess.run(
            f'sudo netctl {cmd} {self.pf_name}', shell=True)


def main():
    # for use with interactive shell
    global data
    data = wifi_data()
    print(data)


if __name__ == '__main__':
    main()
