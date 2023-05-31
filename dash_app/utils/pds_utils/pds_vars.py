pds_benchmark_metrics_files_dir = r'../../resources/pds_benchmark_metrics_files'
aggregate_metrics_filename = '../../resources/PDS/pds_aggregate_result.csv'
pds_dataframe_pickle_file = '../../resources/PDS/pds_dataframe.pkl'
pds_dataframe_cleaned_file = '../../resources/PDS/pds_dataframe_cleaned.pkl'
reuse_rate_output_file = '../../resources/PDS/pds_reuse_rates.pkl'
pds_model_weights_file = '../../resources/PDS/pds_model_weights.pkl'

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
