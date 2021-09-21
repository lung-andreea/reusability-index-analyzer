import os

import pandas as pd

from utils.pds_utils.pds_vars import pds_dataframe_pickle_file, reuse_rate_output_file, pds_dataframe_cleaned_file, \
    pds_model_weights_file, pds_metrics_list


class PdsDataBuilder:
    def construct_weights_dataframe(self):
        metric_weight_list = []
        pds_dataframe = self.get_pds_data_frame()
        reuse_rates_dataframe = self.get_reuse_rates_dataframe()
        reuse_rate_values = reuse_rates_dataframe['reuse_rate']
        for metric in pds_metrics_list:
            metric_values = pds_dataframe[metric]
            correlation_coefficient = metric_values.corr(reuse_rate_values)
            metric_weight_list.append({'metric': metric, 'weight': correlation_coefficient})
        df = pd.DataFrame(metric_weight_list, columns=['metric', 'weight'])
        df.to_pickle(pds_model_weights_file)

    @staticmethod
    def get_model_weights_dict():
        model_weights_records_dict = pd.read_pickle(pds_model_weights_file).to_dict('records')
        return {item['metric']: item['weight'] for item in model_weights_records_dict}

    @staticmethod
    def get_pds_data_frame():
        return pd.read_pickle(pds_dataframe_pickle_file)

    @staticmethod
    def get_reuse_rates_dataframe():
        return pd.read_pickle(reuse_rate_output_file)

    def construct_pds_dataframe_cleaned(self):
        # Get the metrics dataframe with the rows corresponding to components with zero reuse rate eliminated
        reuse_rates_df = self.get_reuse_rates_dataframe()
        zero_reuse_rate_classes = reuse_rates_df[reuse_rates_df.reuse_rate == 0].class_name
        df = self.get_pds_data_frame()
        df = df[~df['LongName'].isin(zero_reuse_rate_classes)]
        print(df)
        df.to_pickle(pds_dataframe_cleaned_file)

    def get_interval_reuse_rate_percentages(self):
        reuse_rates_df = self.get_reuse_rates_dataframe()
        total = len(reuse_rates_df.index)
        pow_two_max = 9
        zero_reuse_rate_classes = reuse_rates_df[reuse_rates_df.reuse_rate == 0]
        zero_reuse_rate_classes_count = len(zero_reuse_rate_classes.index)
        print("ReuseR = 0 | Count:", zero_reuse_rate_classes_count, "Percentage:", zero_reuse_rate_classes_count*100/total)
        for power in range(pow_two_max):
            classes = reuse_rates_df[(reuse_rates_df.reuse_rate >= 2**power) & (reuse_rates_df.reuse_rate < 2**(power+1))]
            classes_count = len(classes.index)
            classes_percentage = classes_count*100/total
            print(f"ReuseR in [{2**power},{2**(power+1)}) | Count:", classes_count, "Percentage:", classes_percentage)
        more_than_two_pow_nine = reuse_rates_df[reuse_rates_df.reuse_rate > 2**pow_two_max]
        more_than_two_pow_nine_count = len(more_than_two_pow_nine.index)
        more_than_two_pow_nine_percentage = more_than_two_pow_nine_count*100/total
        print("ReuseR > 512 | Count:", more_than_two_pow_nine_count, "Percentage:", more_than_two_pow_nine_percentage)

    @staticmethod
    def get_pds_dataframe_cleaned():
        return pd.read_pickle(pds_dataframe_cleaned_file)


