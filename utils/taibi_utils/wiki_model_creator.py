r"""
Utility file to train and save the gensim Word2Vec model
==============================================
Uses the "wiki-english-20171001" corpus
"""

import logging
import gensim.downloader as api

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class WikiModelCreator:
    @staticmethod
    def train_model():
        model = api.load('fasttext-wiki-news-subwords-300')

        print(model.most_similar(positive='integer'))

        model.save("wiki2017.model")




