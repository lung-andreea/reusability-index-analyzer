import os

import pandas as pd


def construct_dataframe_pickle_file(metrics_file, dataframe_output_file):
    data_frame = pd.read_csv(metrics_file, sep=',', low_memory=False)
    data_frame.to_pickle(dataframe_output_file)


def get_enhanced_class_dataframe(class_metrics_file, method_metrics_file):
    class_metrics_df = pd.read_csv(class_metrics_file, sep=',', low_memory=False)
    method_metrics_df = pd.read_csv(method_metrics_file, sep=',', low_memory=False)
    mean_by_class_id_df = method_metrics_df.groupby('Parent').mean().reset_index()
    for index, row in class_metrics_df.iterrows():
        class_id = row['ID']
        method_metrics_df_row = mean_by_class_id_df[mean_by_class_id_df.Parent == class_id]
        avg_complexity_class = 0 if method_metrics_df_row.empty else method_metrics_df_row['McCC'].tolist()[0]
        avg_maintainability_class = 0 if method_metrics_df_row.empty else method_metrics_df_row['MI'].tolist()[0]
        class_metrics_df.at[index, 'ACC'] = avg_complexity_class
        class_metrics_df.at[index, 'MI'] = avg_maintainability_class
    return class_metrics_df


def construct_sample_projects_dataframes(sample_projects_dir):
    sourcemeter_results_dir = f"{sample_projects_dir}/csv_files"
    class_results_dir = f"{sourcemeter_results_dir}/class"
    method_results_dir = f"{sourcemeter_results_dir}/method"
    dataframes_directory = f"{sample_projects_dir}/metrics_dataframes"
    for filename in os.listdir(class_results_dir):
        proj_name = filename[:filename.rfind('-')]
        class_filepath = os.path.join(class_results_dir, filename)
        method_filepath = os.path.join(method_results_dir, f'{proj_name}-Method.csv')
        enhanced_df = get_enhanced_class_dataframe(class_filepath, method_filepath)
        dataframe_output_file = f"{dataframes_directory}/{proj_name}_dataframe.pkl"
        enhanced_df.to_pickle(dataframe_output_file)


# construct_sample_projects_dataframes('../resources/sample_projects_metrics')
