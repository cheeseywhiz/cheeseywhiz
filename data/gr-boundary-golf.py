import json,matplotlib.pyplot as p;p.plot(*zip(*json.loads(open('f').read())['features'][0]['geometry']['coordinates'][0]));p.show()
