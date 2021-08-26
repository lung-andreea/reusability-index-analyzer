import os

import pandas as pd

sample_projects_directory = '../../resources/sample_projects_metrics'
final_results_dir = '../../resources/final_reusability_estimation_results'
sample_projects_dataframes_path_dir = f'{sample_projects_directory}/metrics_dataframes'

projects = ['mockito', 'junit4', 'atmosphere']


def clean_class_name(class_name):
    return class_name[:class_name.find('<')]


def normalize_array(array):
    min_val = min(array)
    max_val = max(array)
    return [(value - min_val) / (max_val - min_val) if max_val != min_val else max_val for value in array]


def get_final_dataframe_columns(properties_list):
    return ['Name', 'Lines of Code', 'Maintainability'] + properties_list + [
               'Reusability Score', 'Version']


def get_class_metrics_dict(dataframe_name, dataframes_path_dir):
    dataframe_path = os.path.join(dataframes_path_dir, dataframe_name)
    class_metrics_dataframe = pd.read_pickle(dataframe_path).to_dict('records')
    return {item['ID']: item for item in class_metrics_dataframe}


def get_property_array_from_class_metrics_dict(class_metrics, property_name):
    return [class_metrics[class_id][property_name] for class_id in class_metrics]


def get_version_from_dataframe_name(dataframe_name):
    project_version_name = dataframe_name.split('_')[0]
    return f"v{project_version_name[project_version_name.find('-') + 1:]}"


def build_single_result_dataframe(dataframe_name, class_metrics, properties_results_dict,
                                  final_reusability_scores_array):
    properties_list = list(properties_results_dict.keys())
    final_dataframe_columns = get_final_dataframe_columns(properties_list)
    version = get_version_from_dataframe_name(dataframe_name)
    names = get_property_array_from_class_metrics_dict(class_metrics, 'Name')
    lines_of_code_array = get_property_array_from_class_metrics_dict(class_metrics, 'LOC')
    maintainability_array = normalize_array(get_property_array_from_class_metrics_dict(class_metrics, 'MI'))
    return pd.DataFrame(
        {'Name': names, 'Lines of Code': lines_of_code_array, 'Maintainability': maintainability_array,
         **properties_results_dict,
         'Reusability Score': final_reusability_scores_array, 'Version': version},
        columns=final_dataframe_columns)
