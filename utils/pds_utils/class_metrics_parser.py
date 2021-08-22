import csv
import os

from utils.pds_utils.pds_vars import pds_metrics_list


def parse_file(filepath, columns):
    row_list = []
    with open(filepath, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            class_metrics_dict = {key: row[key] for key in columns}
            row_list.append(class_metrics_dict)
    return row_list


def parse_directory(directory):
    column_names = ['Name', 'LongName'] + pds_metrics_list
    writer_rows = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        file_rows = parse_file(filepath, column_names)
        writer_rows += file_rows
    with open('../../resources/pds_aggregate_result.csv', 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=column_names)
        writer.writeheader()
        for row in writer_rows:
            writer.writerow(row)


# dir_name = r'../../resources/aggregate_result'
# parse_directory(dir_name)
