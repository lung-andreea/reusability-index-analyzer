import csv

import pandas as pd
import requests

from utils.pds_utils.data_utils import get_pds_data_frame

reuse_rate_output_file = '../../resources/pds_reuse_rates.pkl'

elastic_search_url = "http://localhost:9200/agora/_search"
headers = {"Content-Type": "application/json"}
params = (
    ('pretty', ''),
)


def get_elastic_search_response(class_name):
    payload = ' { "query": { "match_phrase": { "code.imports": "%s" } } } ' % class_name
    return requests.post(elastic_search_url, headers=headers, params=params, data=payload)


def get_class_reuse_rate_pairs():
    df = get_pds_data_frame()
    class_reuse_rates = []
    for class_name in df['LongName'].values:
        elastic_search_query_response = get_elastic_search_response(class_name)
        response_json = elastic_search_query_response.json()
        reuse_rate = response_json['hits']['total']
        class_reuse_rate_dict = {'class_name': class_name, 'reuse_rate': reuse_rate}
        print(class_reuse_rate_dict)
        class_reuse_rates.append(class_reuse_rate_dict)
    return class_reuse_rates


def save_reuse_rates_to_file(output_file, reuse_rate_pair_list):
    df = pd.DataFrame(reuse_rate_pair_list, columns=['class_name', 'reuse_rate'])
    df.to_pickle(output_file)


def run_reuse_rate_service():
    class_reuse_rate_pairs = get_class_reuse_rate_pairs()
    save_reuse_rates_to_file(reuse_rate_output_file, class_reuse_rate_pairs)


run_reuse_rate_service()
