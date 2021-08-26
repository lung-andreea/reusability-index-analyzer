r"""
Utility file to train and save the gensim Word2Vec model
==============================================
Uses the "wiki-english-20171001" corpus
"""

import logging
import inspect
from gensim.models.word2vec import Word2Vec
import gensim.downloader as api

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# corpus = api.load('fasttext-wiki-news-subwords-300')
model = api.load('fasttext-wiki-news-subwords-300')

# print(inspect.getsource(corpus.__class__))
# print(inspect.getfile(corpus.__class__))
#
# model = Word2Vec(corpus, vector_size=100, window=5, min_count=1, workers=4)
print(model.most_similar(positive='integer'))

model.save("wiki2017.model")

