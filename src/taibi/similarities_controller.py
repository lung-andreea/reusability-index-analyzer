import itertools
import os
import re

import statistics
import pandas as pd
from utils.taibi_utils.taibi_util_fns import camel_case_split
from utils.taibi_utils.taibi_vars import srcML_results_file
from utils.taibi_utils.xml_parser import parse_xml_file
from gensim.models.keyedvectors import KeyedVectors

model = KeyedVectors.load('../../resources/Taibi/wiki2017.model')


def format_word(word):
    """
    Returns the list of lower-cased sub-words from a camel-case string
    ==============================================
    :param word: string - the word to be split
    :return: lower camel-case split list of sub-words from the original word
    """
    return [sub_word.lower() for sub_word in camel_case_split(word) if sub_word.lower() in model]


def get_lower_case_camel_case_splitted_list(word_list):
    """
       Returns the flattened lower-cased list of words from a list of words mixing normal words with camel-case words
       ==============================================
       :param word_list: string[] - list of normal-case and camel-case words
       :return: lower normal-case flattened list of words from the original list
       """
    return list(itertools.chain(*[format_word(word) for word in word_list]))


def get_comment_list_cleaned(comment_list):
    """
    Function to get the list of comments split into words
    ==============================================
    :param comment_list: string[] - list of comment strings
    :return: comment_list_cleaned: string[][] - array of string arrays, each representing the comment split into words
                                                example: for "//* "This" is a comment ** \t\n *//"
                                                         => ["this", "is", "a", "comment"]
    """
    return [get_lower_case_camel_case_splitted_list(re.findall(r'\w+', comment_string))
            for comment_string in comment_list]


def get_class_identifier_names_similarity(class_name, identifier_list):
    similarities_array = []
    class_name_word_vec = format_word(class_name)
    for identifier in identifier_list:
        ident_words = format_word(identifier)
        if len(class_name_word_vec) and len(ident_words):
            similarities_array.append(model.n_similarity(class_name_word_vec, ident_words))
    average_similarity = statistics.mean(similarities_array) if len(similarities_array) else 0
    print('Class Name:', class_name, 'Similarity array:', similarities_array, 'Average similarity:',
          average_similarity)
    return average_similarity


def get_comment_identifier_names_similarity(comment_list, identifier_list):
    comment_list_cleaned = get_comment_list_cleaned(comment_list)
    identifier_list_flattened = get_lower_case_camel_case_splitted_list(identifier_list)
    similarities_list = [model.n_similarity([word for word in comment if word in model], identifier_list_flattened) for
                         comment in comment_list_cleaned if len(comment) and len(identifier_list_flattened)]
    return statistics.mean(similarities_list) if len(similarities_list) else 0


def build_single_similarity_file(project_name, class_identifier_dict):
    roi_similarities_dict = {}
    cic_similarities_dict = {}
    for class_name, identifier_comment_dict in class_identifier_dict.items():
        identifier_list = identifier_comment_dict['identifiers']
        comment_list = identifier_comment_dict['comments']
        roi_similarities_dict[class_name] = get_class_identifier_names_similarity(class_name, identifier_list)
        cic_similarities_dict[class_name] = get_comment_identifier_names_similarity(comment_list, identifier_list)
        print('Class Name:', class_name, "Comment Identifiers Similarity:", cic_similarities_dict[class_name])
    df = pd.DataFrame({'Class': list(class_identifier_dict.keys()), 'ROI': list(roi_similarities_dict.values()),
                       'CIC': list(cic_similarities_dict.values())}, columns=['Class', 'ROI', 'CIC'])
    df.to_pickle(f'../../resources/Taibi/similarity_files/{project_name}.pkl')


def build_roi_similarity_files():
    for filename in os.listdir(srcML_results_file):
        filepath = os.path.join(srcML_results_file, filename)
        project_name = filename[:filename.find('.xml')]
        class_identifier_comments_dict = parse_xml_file(filepath)
        build_single_similarity_file(project_name, class_identifier_comments_dict)


build_roi_similarity_files()
