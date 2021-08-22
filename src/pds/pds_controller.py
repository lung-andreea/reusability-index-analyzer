import os

import numpy as np
import pandas as pd

from utils.pds_utils.data_utils import get_model_weights_dict
from utils.pds_utils.pds_vars import pds_metrics_list, property_metrics_dict, pds_model_weights_file, final_results_dir, \
    sample_projects_directory


class PdsController:
    def __init__(self, project_names, dataframes_path_dir):
        self.project_names = project_names
        self.dataframes_path_dir = dataframes_path_dir
        self.model_weights = get_model_weights_dict()
        self.polynomial_models = {
            metric: np.poly1d(np.load(f'../../resources/pds_regression_models/{metric}_model.npy')) for metric in
            pds_metrics_list}

    @staticmethod
    def get_class_metrics_dict(dataframe_path):
        class_metrics_dataframe = pd.read_pickle(dataframe_path).to_dict('records')
        return {item['ID']: item for item in class_metrics_dataframe}

    @staticmethod
    def get_final_dataframe_columns(properties_list):
        return ['Name', 'Lines of Code'] + list(
            map(lambda property_nm: property_nm.capitalize(), properties_list)) + [
                   'Reusability Score', 'Version']

    def get_metric_score(self, metric_name, metric_value):
        return self.polynomial_models[metric_name](metric_value)

    def calculate_score_per_property(self, property_name, class_metrics):
        return sum(map(lambda metric_name: self.model_weights[metric_name] * self.get_metric_score(metric_name,
                                                                                                   class_metrics[
                                                                                                       metric_name]),
                       property_metrics_dict[property_name])) / sum(
            self.model_weights[metric_name] for metric_name in property_metrics_dict[property_name])

    def calculate_final_score_per_class(self, class_metrics):
        return 1 / len(property_metrics_dict) * sum(
            self.calculate_score_per_property(property_name, class_metrics) for property_name in property_metrics_dict)

    def build_single_result_dataframe(self, dataframe_name):
        properties_list = list(property_metrics_dict.keys())
        final_dataframe_columns = self.get_final_dataframe_columns(properties_list)
        dataframe_name_parts = dataframe_name.split('_')
        version = dataframe_name_parts[1]
        dataframe_path = os.path.join(self.dataframes_path_dir, dataframe_name)
        class_metrics = self.get_class_metrics_dict(dataframe_path)
        names = [class_metrics[class_id]['Name'] for class_id in class_metrics]
        lines_of_code_array = [class_metrics[class_id]['LOC'] for class_id in class_metrics]
        properties_results = {property_name: [] for property_name in properties_list}
        for class_id in class_metrics:
            for property_name in properties_list:
                score_per_property = self.calculate_score_per_property(property_name, class_metrics[class_id])
                properties_results[property_name].append(score_per_property)
        final_reusablity_scores = [self.calculate_final_score_per_class(class_metrics[class_id]) for class_id in
                                   class_metrics]
        properties_results_keys_capitalized = {k.capitalize(): v for k, v in properties_results.items()}
        return pd.DataFrame({'Name': names, 'Lines of Code': lines_of_code_array, **properties_results_keys_capitalized,
                             'Reusability Score': final_reusablity_scores, 'Version': version},
                            columns=final_dataframe_columns)

    def build_final_result_file(self):
        properties_list = list(property_metrics_dict.keys())
        final_dataframe_columns = self.get_final_dataframe_columns(properties_list)
        final_dataframes_dict = {project_name: pd.DataFrame(columns=final_dataframe_columns) for project_name in
                                 self.project_names}
        for dataframe_name in os.listdir(self.dataframes_path_dir):
            proj = dataframe_name.split('_')[0]
            df = self.build_single_result_dataframe(dataframe_name)
            final_dataframes_dict[proj] = final_dataframes_dict[proj].append(df, ignore_index=True, sort=False)
        for project_name, final_project_dataframe in final_dataframes_dict.items():
            print(final_project_dataframe)
            final_project_dataframe.to_pickle(f'{final_results_dir}/PDS/{project_name}_results.pkl')


projects = ['mockito', 'junit4', 'atmosphere']
# dataframes_path_dir = f'{sample_projects_directory}/metrics_dataframes/PDS'
# pds_controller = PdsController(projects, dataframes_path_dir)
# pds_controller.build_final_result_file()

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

for project_name in projects:
    print(f'----------------- {project_name} -----------------')
    df = pd.read_pickle(f'{final_results_dir}/PDS/{project_name}_results.pkl')
    print(df[PdsController.get_final_dataframe_columns(list(property_metrics_dict.keys()))])
