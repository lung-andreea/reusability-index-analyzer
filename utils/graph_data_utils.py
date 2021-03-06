import pandas as pd
import re

projects = ['Mockito', 'JUnit4', 'Atmosphere']
models = ['PDS', 'Taibi', 'QMOOD']
capitalized_to_lowercase_project_names = {'Mockito': 'mockito', 'JUnit4': 'junit4', 'Atmosphere': 'atmosphere'}
final_results_folder_path = './resources/final_reusability_estimation_results'
popularity_metrics = {'Mockito': {'used-by': '107k', 'stars': '8.2k', 'mvn-downloads': '24k'},
                      'JUnit4': {'used-by': '1.8m', 'stars': '12.1k', 'mvn-downloads': '109k'},
                      'Atmosphere': {'used-by': '134', 'stars': '3.5k', 'mvn-downloads': '275'}}


class GraphDataHandler:
    @staticmethod
    def natural_sort(ls):
        def convert(text):
            return int(text) if text.isdigit() else text.lower()

        return sorted(ls, key=lambda key: [convert(c) for c in re.split('([0-9]+)', key)])

    @staticmethod
    def get_class_reusability_dataframes():
        return {model: {project_name: pd.read_pickle(
            f'{final_results_folder_path}/{model}/{capitalized_to_lowercase_project_names[project_name]}_results.pkl'
        ) for project_name in projects} for model in models}

    @staticmethod
    def format_reusability_tile_info(value):
        return f'{str(round(value * 100, 2))}%'

    def get_min_max_average_reusability(self, selected_project, selected_model, selected_version):
        class_reusability_dataframes = self.get_class_reusability_dataframes()
        selected_project_dataframe = class_reusability_dataframes[selected_model][selected_project]
        filtered_df = selected_project_dataframe[selected_project_dataframe.Version == selected_version]
        reusability_score_column = filtered_df['Reusability Score']
        return self.format_reusability_tile_info(reusability_score_column.min()), self.format_reusability_tile_info(
            reusability_score_column.max()), self.format_reusability_tile_info(reusability_score_column.mean())

    def get_project_versions_info(self):
        class_reusability_dataframes = self.get_class_reusability_dataframes()

        junit4_versions = self.natural_sort(class_reusability_dataframes['PDS']['JUnit4']['Version'].unique())
        mockito_versions = self.natural_sort(class_reusability_dataframes['PDS']['Mockito']['Version'].unique())
        atmosphere_versions = self.natural_sort(class_reusability_dataframes['PDS']['Atmosphere']['Version'].unique())

        number_of_versions_per_project = {'Mockito': len(mockito_versions), 'JUnit4': len(junit4_versions),
                                          'Atmosphere': len(atmosphere_versions)}
        versions_chart_max_dist = max(number_of_versions_per_project.values()) * 0.5
        version_label_index_dict_mockito = {
            mockito_versions[i]: (i + 1) * (versions_chart_max_dist / number_of_versions_per_project['Mockito']) for i
            in range(number_of_versions_per_project['Mockito'])}
        version_label_index_dict_junit4 = {
            junit4_versions[i]: (i + 1) * (versions_chart_max_dist / number_of_versions_per_project['JUnit4']) for i
            in range(number_of_versions_per_project['JUnit4'])}
        version_label_index_dict_atmosphere = {
            atmosphere_versions[i]: (i + 1) * (versions_chart_max_dist / number_of_versions_per_project['Atmosphere']) for i
            in range(number_of_versions_per_project['Atmosphere'])}
        version_label_to_index_dict = {'Mockito': version_label_index_dict_mockito,
                                       'JUnit4': version_label_index_dict_junit4,
                                       'Atmosphere': version_label_index_dict_atmosphere}
        return version_label_to_index_dict

    def get_selected_version_for_project(self, project_name, version_number=None, version_index=None):
        version_info = self.get_project_versions_info()
        selected_project_versions_dict = version_info[project_name]
        selected_project_versions_dict_keys = list(selected_project_versions_dict.keys())
        selected_project_versions_dict_values = list(selected_project_versions_dict.values())
        selected_index = version_index if version_index is not None else selected_project_versions_dict_values.index(
            version_number)
        return selected_project_versions_dict_keys[selected_index]

    def get_selected_version_index(self, project_name, version_number):
        version_info = self.get_project_versions_info()
        selected_project_versions_dict = version_info[project_name]
        selected_project_versions_dict_values = list(selected_project_versions_dict.values())
        return selected_project_versions_dict_values.index(version_number)

    def get_average_reusability_dataframe(self):
        class_reusability_dataframes = self.get_class_reusability_dataframes()
        version_info = self.get_project_versions_info()
        average_reusability_pairs = []
        for project in projects:
            version_dict = version_info[project]
            for model in models:
                class_reusability_dataframe = class_reusability_dataframes[model][project]
                for version_label in version_dict:
                    mean_reusability_per_version = \
                        class_reusability_dataframe[class_reusability_dataframe.Version == version_label][
                            'Reusability Score'].mean()
                    average_reusability_pairs.append(
                        (project, model, version_dict[version_label], mean_reusability_per_version))
        avg_reusability_df = pd.DataFrame(average_reusability_pairs,
                                          columns=['Project', "Reusability Model", "Version", "Average Reusability Score"])
        return avg_reusability_df

    def get_reusability_per_number_of_classes_distributions(self, selected_project, selected_version):
        class_reusability_dataframes = self.get_class_reusability_dataframes()
        distribution_per_model_dict = {}
        for model in models:
            df = class_reusability_dataframes[model][selected_project]
            filtered_by_version_df = df[df.Version == selected_version]
            reusability_score_column = filtered_by_version_df['Reusability Score']
            distribution_per_model_dict[model] = reusability_score_column
        return distribution_per_model_dict

    def get_average_quality_factors_df(self, selected_project, selected_model):
        class_reusability_dataframes = self.get_class_reusability_dataframes()
        df = class_reusability_dataframes[selected_model][selected_project]
        return df.groupby('Version').mean().reset_index()

    def get_average_maintainability_complexity_documentation(self, selected_project):
        final_dataframe = pd.DataFrame(
            columns=['Reusability', 'Maintainability', 'Documentation', 'Complexity', 'Version', 'Model'])
        class_reusability_dataframes = self.get_class_reusability_dataframes()
        for model in models:
            df = class_reusability_dataframes[model][selected_project]
            number_of_versions = len(df.Version.unique())
            model_series = pd.Series([model for _ in range(number_of_versions)])
            cc_series = df['Cyclomatic Complexity']
            df_filtered = pd.DataFrame(
                {'Reusability': df['Reusability Score'], 'Maintainability': df.Maintainability,
                 'Documentation': df['Documentation (Comment Density)'],
                 'Complexity': (cc_series - cc_series.min()) / (cc_series.max() - cc_series.min()),
                 'Version': df.Version})
            mean_df = df_filtered.groupby('Version').mean().reset_index()
            mean_df['Model'] = model_series
            final_dataframe = final_dataframe.append(mean_df, ignore_index=True, sort=False)
        return final_dataframe
