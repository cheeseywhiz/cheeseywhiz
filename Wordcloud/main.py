#!/usr/bin/env python3
import os
import sys
import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS

IMG_NAME = os.path.abspath('mask.png')
WC_NAME = os.path.abspath('wordcloud.png')
WIDTH = 1920
HEIGHT = 1080
STOPWORDS_ = set(STOPWORDS)
EXTRA_WORDS = [
    'Louie', 'Eric', 'Blair', 'George', 'Orwell', 'telephone', 'interview',
    'Chapter', 'Page',
]

for word in EXTRA_WORDS:
    STOPWORDS_.add(word)

# Build wordcloud on top of black 1920x1080 image
Image.new('RGB', (WIDTH, HEIGHT)).save(IMG_NAME)
img_mask = np.array(Image.open(IMG_NAME))

output_directory = os.path.abspath(sys.argv[1])
files = [output_directory + '/' + file
         for file in os.listdir(output_directory)]

text = []
for file in files:
    with open(file) as f:
        text.append(f.read())

text = ' '.join(text)

wordcloud = WordCloud(
    background_color='white',
    stopwords=STOPWORDS_,
    mask=img_mask,
)
wordcloud.generate(text).to_file(WC_NAME)

print('done')
