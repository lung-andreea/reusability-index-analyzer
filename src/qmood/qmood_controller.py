import os

import pandas as pd

from utils.global_vars_fns import projects, final_results_dir, get_class_metrics_dict, \
    get_final_dataframe_columns, build_single_result_dataframe, sample_projects_dataframes_path_dir, \
    get_property_array_from_class_metrics_dict, normalize_array
from utils.qmood_utils.qmood_vars import property_metrics_dict


class QMOODController:
    def __init__(self, project_names, df_paths_dir):
        self.project_names = project_names
        self.dataframes_path_dir = df_paths_dir

    @staticmethod
    def get_score_per_metric_array(metric_name, class_metrics):
        return {
            'CAM': [1 - lcom_value for lcom_value in
                    get_property_array_from_class_metrics_dict(class_metrics, 'LCOM5')],
            'CBO': get_property_array_from_class_metrics_dict(class_metrics, 'CBO'),
            'NPM': get_property_array_from_class_metrics_dict(class_metrics, 'NPM'),
            'LLOC': get_property_array_from_class_metrics_dict(class_metrics, 'LLOC')
        }.get(metric_name, 0)

    @staticmethod
    def calculate_final_score_per_class(coupling_values, cohesion_values, messaging_values, design_size_values):
        return [-0.25 * coupling + 0.25 * cohesion + 0.5 * messaging + 0.5 * design_size for
                coupling, cohesion, messaging, design_size in
                zip(coupling_values, cohesion_values, messaging_values, design_size_values)]

    def build_single_result_dataframe(self, dataframe_name):
        properties_list = list(property_metrics_dict.keys())
        class_metrics = get_class_metrics_dict(dataframe_name, self.dataframes_path_dir)
        properties_results = {property_name: [] for property_name in properties_list}
        for property_name in properties_list:
            properties_results[property_name] = normalize_array(
                self.get_score_per_metric_array(property_metrics_dict[property_name][0],
                                                class_metrics))
        final_reusablity_scores = self.calculate_final_score_per_class(properties_results['Coupling'],
                                                                       properties_results['Cohesion'],
                                                                       properties_results['Messaging'],
                                                                       properties_results[
                                                                           'Design Size'])
        return build_single_result_dataframe(dataframe_name, class_metrics, properties_results,
                                             final_reusablity_scores)

    def build_final_result_file(self):
        final_dataframe_columns = get_final_dataframe_columns(list(property_metrics_dict.keys()))
        final_dataframes_dict = {project_name: pd.DataFrame(columns=final_dataframe_columns) for project_name in
                                 self.project_names}
        for dataframe_name in os.listdir(self.dataframes_path_dir):
            project_version_name = dataframe_name.split('_')[0]
            proj = project_version_name[:project_version_name.find('-')]
            df = self.build_single_result_dataframe(dataframe_name)
            final_dataframes_dict[proj] = final_dataframes_dict[proj].append(df, ignore_index=True, sort=False)
        for proj_name, final_project_dataframe in final_dataframes_dict.items():
            print(final_project_dataframe)
            final_project_dataframe.to_pickle(f'{final_results_dir}/QMOOD/{proj_name}_results.pkl')


qmood_controller = QMOODController(projects, sample_projects_dataframes_path_dir)
qmood_controller.build_final_result_file()

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)
# pd.set_option("display.max_rows", None)

for project_name in projects:
    print(f'----------------- {project_name} -----------------')
    df = pd.read_pickle(f'{final_results_dir}/QMOOD/{project_name}_results.pkl')
    print(df[get_final_dataframe_columns(list(property_metrics_dict.keys()))])
