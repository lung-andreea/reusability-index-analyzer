import pandas as pd

from src.model_controller import ModelController
from src.taibi.similarities_controller import SimilaritiesController
from src.utils.taibi_utils.taibi_util_fns import get_lcom_weight, get_cbo_weight, get_cc_weight, get_nm_weight, \
    get_dit_weight
from utils.taibi_utils.taibi_vars import property_metrics_dict, factors_tuning_parameters, metrics_tuning_parameters, \
    similarity_files_dir


class TaibiController(ModelController):
    def __init__(self, project_names, df_paths_dir, model_name, properties_dict):
        super().__init__(project_names, df_paths_dir)
        self.model_name = model_name
        self.property_metrics_dict = properties_dict
        self.similarties_controller = SimilaritiesController()

    @staticmethod
    def get_metric_weights(metric_name, metric_value):
        return {
            'LCOM5': get_lcom_weight(metric_value),
            'CBO': get_cbo_weight(metric_value),
            'ACC': get_cc_weight(metric_value),
            'NM': get_nm_weight(metric_value),
            'DIT': get_dit_weight(metric_value)
        }.get(metric_name, 0)

    def calculate_weighted_factor_score(self, class_metrics_dict, factor):
        return sum(
            metrics_tuning_parameters[metric] * self.get_metric_weights(metric, class_metrics_dict[metric]) for metric
            in self.property_metrics_dict[factor]) / sum(
            metrics_tuning_parameters[metric] for metric in self.property_metrics_dict[factor])

    def get_understandability_score(self, dataframe_name, class_metrics):
        self.similarties_controller.build_roi_similarity_files()
        project_name = dataframe_name.split('_')[0]
        similarity_dict_list = pd.read_pickle(f"{similarity_files_dir}/{project_name}.pkl").to_dict('records')
        class_ids = self.dataframe_data_handler.get_property_array_from_class_metrics_dict(class_metrics, 'ID')
        class_names = self.dataframe_data_handler.get_property_array_from_class_metrics_dict(class_metrics, 'Name')
        understandability_scores = {class_id: 0 for class_id in class_ids}
        for similarity_tuple in similarity_dict_list:
            relevance_of_identifiers = similarity_tuple['ROI']
            correlation_identifiers_comments = similarity_tuple['CIC']
            if similarity_tuple['Class'] in class_names:
                class_index = class_names.index(similarity_tuple['Class'])
                class_id = class_ids[class_index]
                understandability_scores[class_id] = (relevance_of_identifiers + correlation_identifiers_comments) / 2
        return understandability_scores

    @staticmethod
    def get_final_class_reusability_score(factor_values_dict):
        return sum(
            factors_tuning_parameters[factor] * factor_values_dict[factor] for factor in property_metrics_dict.keys())

    def build_single_result_dataframe(self, dataframe_name):
        properties_list = list(self.property_metrics_dict.keys())
        class_metrics = self.dataframe_data_handler.get_class_metrics_dict(dataframe_name, self.dataframes_path_dir)
        properties_results = {property_name: [] for property_name in properties_list}
        final_scores_per_class = []
        understandability_scores = self.get_understandability_score(dataframe_name, class_metrics)
        for class_id in class_metrics:
            class_modularity_score = self.calculate_weighted_factor_score(class_metrics[class_id], 'Modularity')
            class_low_complexity_score = self.calculate_weighted_factor_score(class_metrics[class_id], 'Low Complexity')
            properties_results['Modularity'].append(class_modularity_score)
            properties_results['Understandability'].append(understandability_scores[class_id])
            properties_results['Low Complexity'].append(class_low_complexity_score)
            final_scores_per_class.append(
                self.get_final_class_reusability_score(
                    {'Modularity': class_modularity_score, 'Understandability': understandability_scores[class_id],
                     'Low Complexity': class_low_complexity_score}))
        return self.dataframe_data_handler.build_single_result_dataframe(dataframe_name, class_metrics,
                                                                         properties_results,
                                                                         final_scores_per_class)
