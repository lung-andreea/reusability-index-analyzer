import pandas as pd

from src.model_controller import ModelController
from utils.global_vars_fns import projects, sample_projects_dataframes_path_dir, normalize_array, \
    final_results_dir, DataframeDataHandler
from utils.qmood_utils.qmood_vars import property_metrics_dict


class QMOODController(ModelController):
    def __init__(self, project_names, df_paths_dir, model_name, properties_dict):
        super().__init__(project_names, df_paths_dir)
        self.model_name = model_name
        self.property_metrics_dict = properties_dict

    def get_score_per_metric_array(self, metric_name, class_metrics):
        return {
            'CAM': [1 - lcom_value for lcom_value in
                    self.dataframe_data_handler.get_property_array_from_class_metrics_dict(class_metrics, 'LCOM5')],
            'CBO': self.dataframe_data_handler.get_property_array_from_class_metrics_dict(class_metrics, 'CBO'),
            'NPM': self.dataframe_data_handler.get_property_array_from_class_metrics_dict(class_metrics, 'NPM'),
            'LLOC': self.dataframe_data_handler.get_property_array_from_class_metrics_dict(class_metrics, 'LLOC')
        }.get(metric_name, 0)

    @staticmethod
    def calculate_final_score_per_class(coupling_values, cohesion_values, messaging_values, design_size_values):
        return [-0.25 * coupling + 0.25 * cohesion + 0.5 * messaging + 0.5 * design_size for
                coupling, cohesion, messaging, design_size in
                zip(coupling_values, cohesion_values, messaging_values, design_size_values)]

    def build_single_result_dataframe(self, dataframe_name):
        properties_list = list(self.property_metrics_dict.keys())
        class_metrics = self.dataframe_data_handler.get_class_metrics_dict(dataframe_name, self.dataframes_path_dir)
        properties_results = {property_name: [] for property_name in properties_list}
        for property_name in properties_list:
            properties_results[property_name] = normalize_array(
                self.get_score_per_metric_array(self.property_metrics_dict[property_name][0],
                                                class_metrics))
        final_reusablity_scores = self.calculate_final_score_per_class(properties_results['Coupling'],
                                                                       properties_results['Cohesion'],
                                                                       properties_results['Messaging'],
                                                                       properties_results[
                                                                           'Design Size'])
        return self.dataframe_data_handler.build_single_result_dataframe(dataframe_name, class_metrics, properties_results,
                                             final_reusablity_scores)


