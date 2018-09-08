import collect
import json

data = {
    'dirs': {
        'recursive': ([
            '~/Pictures'
        ], {
            'cfg': '~/.config'
        }),

        'nonrecursive': ([
            '/etc'
        ], {
            'home': '~'
        }),

        'ignore': [
            '../.git'
        ]
    },
    'static': ([
        'myStyle.css'
    ], {
        'img.png': '~/Pictures/wallpapers/tikkle7e9qhz.jpg'
    })
}


def _update_from_data_tree(self, tree):
    for path in tree['dirs']['recursive'][0]:
        dir_path = collect.path.Path(path)
        self[dir_path.basename] = dir_path

    self.update(tree['dirs']['recursive'][1])

    for path in tree['dirs']['nonrecursive'][0]:
        dir_path = collect.path.Path(path)
        self[dir_path.basename] = dir_path, False

    for url, path in tree['dirs']['nonrecursive'][1].items():
        self[url] = path, False

    self.exclude(*tree['dirs']['ignore'])

    for path in tree['static'][0]:
        file_path = collect.path.Path(path)
        self[file_path.basename] = file_path

    self.update(tree['static'][1])
    return self


def update_from_files_json(self, path):
    with open(path) as file:
        data = json.load(file)

    return _update_from_data_tree(self, data)
