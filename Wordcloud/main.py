#!/usr/bin/env python3
import os
import sys
import matplotlib.pyplot as plt
from wordcloud import WordCloud

text = []
dir = os.path.abspath(sys.argv[1])
files = [dir + '/' + file
         for file in os.listdir(dir)]

for file in files:
    with open(file) as f:
        text.append(f.read())

text = ' '.join(text)

wordcloud = WordCloud().generate(text)

image_args = [wordcloud, ]
image_kwargs = {'interpolation': 'quadric', }
plt.axis('off')
plt.imshow(*image_args, **image_kwargs)
plt.savefig('wordcloud.png')
plt.show()
