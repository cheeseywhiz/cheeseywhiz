import matplotlib.pyplot as p
import json
p.plot(*zip(*json.loads(open('f').read())['features'][0]['geometry']['coordinates'][0]));p.show()
