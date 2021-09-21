import numpy as np
import pandas as pd

from src.model_controller import ModelController
from src.pds.pds_model import PdsModel
from src.pds.reuse_rate_controller import ReuseRateController
from utils.global_vars_fns import final_results_dir, projects, sample_projects_dataframes_path_dir, \
    construct_dataframe_pickle_file, DataframeDataHandler
from utils.pds_utils.class_metrics_parser import ClassMetricsParser
from utils.pds_utils.data_utils import PdsDataBuilder
from utils.pds_utils.pds_vars import pds_metrics_list, property_metrics_dict, pds_benchmark_metrics_files_dir, \
    aggregate_metrics_filename, pds_dataframe_pickle_file


class PdsController(ModelController):
    def __init__(self, project_names, df_paths_dir, model_name, properties_dict):
        super().__init__(project_names, df_paths_dir)
        self.model_name = model_name
        self.property_metrics_dict = properties_dict
        self.class_metrics_parser = ClassMetricsParser()
        self.reuse_rate_controller = ReuseRateController()
        self.pds_model = PdsModel()
        self.data_builder = PdsDataBuilder()
        self.build_polynomial_models()
        self.model_weights = self.dataframe_data_handler.get_model_weights_dict()
        self.polynomial_models = {
            metric: np.poly1d(np.load(f'../../resources/PDS/pds_regression_models/{metric}_model.npy')) for metric in
            pds_metrics_list}

    @staticmethod
    def build_polynomial_models(self):
        # Parse the directory containing the metrics files produced by Sourcemeter for the pds benchmark projects and
        # build a single file containing all the results
        self.class_metrics_parser.parse_directory(pds_benchmark_metrics_files_dir)
        construct_dataframe_pickle_file(aggregate_metrics_filename, pds_dataframe_pickle_file)
        # Run reuse rate service to build reuse rate file - we will then use that to eliminate classes with 0 reuse rate
        self.reuse_rate_controller.run_reuse_rate_service()
        # Build the cleaned version of the pds dataframe - that is - the dataframe containing all the class results of
        # the pds benchmark projects, if the class reuse rate is not 0
        self.data_builder.construct_pds_dataframe_cleaned()
        self.data_builder.construct_weights_dataframe()
        # Build the bin reusability scores dataframe - for each metric, the corresponding bins
        # and the reusability scores assigned to them
        self.pds_model.build_metrics_general_distribution()
        # Create the regression models for each metric and save them to their respective .npy file
        self.pds_model.build_regression_models()

    def get_metric_score(self, metric_name, metric_value):
        return self.polynomial_models[metric_name](metric_value)

    def calculate_score_per_property(self, property_name, class_metrics):
        return sum(map(lambda metric_name: self.model_weights[metric_name] * self.get_metric_score(metric_name,
                                                                                                   class_metrics[
                                                                                                       metric_name]),
                       self.property_metrics_dict[property_name])) / sum(
            self.model_weights[metric_name] for metric_name in self.property_metrics_dict[property_name])

    def calculate_final_score_per_class(self, class_metrics):
        return 1 / len(self.property_metrics_dict) * sum(
            self.calculate_score_per_property(property_name, class_metrics) for property_name in
            self.property_metrics_dict)

    def build_single_result_dataframe(self, dataframe_name):
        properties_list = list(self.property_metrics_dict.keys())
        class_metrics = self.dataframe_data_handler.get_class_metrics_dict(dataframe_name, self.dataframes_path_dir)
        properties_results = {property_name: [] for property_name in properties_list}
        for class_id in class_metrics:
            for property_name in properties_list:
                score_per_property = self.calculate_score_per_property(property_name, class_metrics[class_id])
                properties_results[property_name].append(score_per_property)
        final_reusablity_scores = [self.calculate_final_score_per_class(class_metrics[class_id]) for class_id in
                                   class_metrics]
        properties_results_keys_capitalized = {k.capitalize(): v for k, v in properties_results.items()}
        return self.dataframe_data_handler.build_single_result_dataframe(dataframe_name, class_metrics,
                                                                         properties_results_keys_capitalized,
                                                                         final_reusablity_scores)

