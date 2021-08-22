import csv
from math import sqrt

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from utils.pds_utils.data_utils import get_pds_dataframe_cleaned, get_reuse_rates_dataframe
from utils.pds_utils.pds_vars import pds_metrics_list

aggregate_metrics_filename = '../../resources/pds_aggregate_result.csv'
bin_reusability_scores_file = '../../resources/bin_reusability_scores.pkl'
polynomial_degrees_file = '../../resources/polynomial_degrees.csv'
polynomial_models_directory = '../../resources/pds_regression_models'


class PdsModel:
    def __init__(self):
        self.data_frame = get_pds_dataframe_cleaned()
        self.data_sample_size = len(self.data_frame.index)
        # Dictionary of the form:
        # { metric_name: { bin_0_center: reusability_score(bin0), bin_1_center: reusability_score(bin1) ... } ... }
        # Where bin_k_center is the center (middle value) of the k-th bin corresponding to the given metric
        self.reusability_scores = {}

    @staticmethod
    def get_poly_model(x, y, degree):
        return np.poly1d(np.polyfit(x, y, degree))

    @staticmethod
    def get_rmse(y, y_pred):
        return np.sqrt(mean_squared_error(y, y_pred))

    # Returns the optimal bin_width for a given metric
    def get_metric_bin_width(self, metric):
        values_mean = self.data_frame[metric].mean()
        standard_deviation = sqrt(
            sum([(value - values_mean) ** 2 for value in self.data_frame[metric].values]) / self.data_sample_size)
        bin_width = 3.49 * standard_deviation * self.data_sample_size ** (-1 / 3)
        print("Metric:", metric, "Std. deviation:", standard_deviation, "Bin width:", bin_width)
        return bin_width

    def build_metrics_general_distribution(self):
        reuse_rates_records_dict = get_reuse_rates_dataframe().to_dict('records')
        reuse_rates_dict = {item['class_name']: item['reuse_rate'] for item in reuse_rates_records_dict}
        for metric in pds_metrics_list:
            bin_width = self.get_metric_bin_width(metric)
            max_metric_value = self.data_frame[metric].max()
            last_bin_index = int(max_metric_value // bin_width)
            bin_info_dict = {}
            for bin_index in range(0, last_bin_index + 1):
                bin_start = bin_index * bin_width
                bin_end = (bin_index + 1) * bin_width
                bin_center = (bin_start + bin_end) / 2
                bin_reusability_score = sum(
                    int(reuse_rates_dict[val]) for val in self.data_frame.loc[
                        (self.data_frame[metric] >= bin_start) & (self.data_frame[metric] < bin_end)][
                        'LongName'].values)
                bin_info_dict[bin_center] = bin_reusability_score
                print("Metric:", metric, " | Bin: ", [bin_start, bin_end],
                      " | Reusability Score: ", bin_reusability_score)
            min_score = min(bin_info_dict.values())
            max_score = max(bin_info_dict.values())
            bin_info_dict_normalized = {bin[0]: (bin[1] - min_score) / (max_score - min_score) for bin in
                                        bin_info_dict.items()}
            self.reusability_scores[metric] = bin_info_dict_normalized
        reusability_scores_df_data = [(item[0], bin_info[0], bin_info[1]) for item in self.reusability_scores.items()
                                      for
                                      bin_info in item[1].items()]
        df = pd.DataFrame(reusability_scores_df_data, columns=["metric", "bin_center", "reusability_score"])
        print(df)
        df.to_pickle(bin_reusability_scores_file)

    def build_regression_models(self):
        polynomial_degrees_dict = {}
        with open(polynomial_degrees_file, mode='r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                polynomial_degrees_dict[row[0]] = row[1]
        bin_reusability_scores_data = pd.read_pickle(bin_reusability_scores_file)
        for metric in polynomial_degrees_dict:
            x, y = self.get_polynomial_regression_train_data(metric, bin_reusability_scores_data)
            poly_model = PdsModel.get_poly_model(x, y, int(polynomial_degrees_dict[metric]))
            np.save(f'{polynomial_models_directory}/{metric}_model.npy', poly_model)

    @staticmethod
    def get_polynomial_regression_train_data(metric, bin_reusability_scores_data):
        train_data = bin_reusability_scores_data[bin_reusability_scores_data["metric"] == metric]
        x = train_data.bin_center.to_numpy()
        y = train_data.reusability_score.to_numpy()
        return x, y

    def plot_rmse_for_each_metric(self):
        bin_reusability_scores_data = pd.read_pickle(bin_reusability_scores_file)
        for metric in pds_metrics_list:
            x, y = self.get_polynomial_regression_train_data(metric, bin_reusability_scores_data)
            self.plot_rmse_range(metric, x, y)

    @staticmethod
    def plot_rmse_range(metric_name, x, y):
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33)
        polynomial_degrees = range(2, 40)
        rmse_values_whole_dataset = []
        rmse_values_train = []
        rmse_values_test = []
        for degree in polynomial_degrees:
            whole_dataset_model = PdsModel.get_poly_model(x, y, degree)
            reg_model = PdsModel.get_poly_model(x_train, y_train, degree)
            y_predicted = whole_dataset_model(x)
            y_train_predicted = reg_model(x_train)
            y_test_predicted = reg_model(x_test)
            rmse_whole_dataset = PdsModel.get_rmse(y, y_predicted)
            rmse_train = PdsModel.get_rmse(y_train, y_train_predicted)
            rmse_test = PdsModel.get_rmse(y_test, y_test_predicted)
            rmse_values_whole_dataset.append(rmse_whole_dataset)
            rmse_values_train.append(rmse_train)
            rmse_values_test.append(rmse_test)
        plt.plot(polynomial_degrees, rmse_values_train, 'bo-', label='Training error')
        plt.plot(polynomial_degrees, rmse_values_test, 'ro-', label='Testing error')
        plt.plot(polynomial_degrees, rmse_values_whole_dataset, 'go-', label='Whole dataset error')
        plt.xlabel('Polynomial degree')
        plt.ylabel(f'RMSE - {metric_name}')
        plt.legend()
        plt.show()

    @staticmethod
    def plot_polynomial_models_degrees(metric_name, x, y):
        polynomial_degrees = range(2, 10)
        plt.plot(x, y, 'or', markersize=1.5)
        for degree in polynomial_degrees:
            reg_model = PdsModel.get_poly_model(x, y, degree)
            y_predicted = reg_model(x)
            plt.plot(x, y_predicted, 'o-', markersize=1.5, label=f"degree = {degree}")
        plt.title(f'{metric_name} model')
        plt.legend()
        plt.show()


pds_model = PdsModel()
pds_model.build_metrics_general_distribution()
pds_model.build_regression_models()
