aggregate_metrics_filename = '../../resources/pds_aggregate_result.csv'
pds_dataframe_pickle_file = '../../resources/pds_dataframe.pkl'
pds_dataframe_cleaned_file = '../../resources/pds_dataframe_cleaned.pkl'
reuse_rate_output_file = '../../resources/pds_reuse_rates.pkl'
pds_model_weights_file = '../../resources/pds_model_weights.pkl'
sample_projects_directory = '../../resources/pds_sample_projects'
final_results_dir = '../../resources/final_reusability_estimation_results'

property_metrics_dict = {'cohesion': ['LCOM5'], 'complexity': ['NL', 'NLE', 'WMC'],
                         'coupling': ['CBO', 'CBOI', 'NII', 'NOI', 'RFC'],
                         'documentation': ['AD', 'CD', 'TCD', 'CLOC', 'TCLOC', 'DLOC', 'PDA', ],
                         'inheritance': ['DIT'],
                         'size': ['LOC', 'LLOC', 'TLLOC', 'TNA', 'NG', 'TNG', 'TNM', 'TNOS', 'TNPM']}

pds_metrics_list = {'LCOM5', 'NL', 'NLE', 'WMC', 'CBO',
                    'CBOI', 'NII', 'NOI', 'RFC', 'AD',
                    'CD', 'TCD', 'CLOC', 'TCLOC', 'DLOC',
                    'PDA', 'DIT', 'LOC', 'LLOC', 'TLLOC',
                    'TNA', 'NG', 'TNG', 'TNM', 'TNOS', 'TNPM'}
