import re


def camel_case_split(identifier):
    if identifier is not None:
        matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return [m.group(0) for m in matches]
    return []


def get_lcom_weight(value):
    return 1 if value == 0 else 0.75 if 0 < value < 3 else 0.5 if 3 <= value < 5 else 0.25 if 5 <= value <= 10 else 0


def get_cbo_weight(value):
    return 1 if value <= 5 else 0.75 if 5 < value <= 7 else 0.5 if 7 < value <= 9 else 0.25 if 9 < value <= 10 else 0


def get_cc_weight(value):
    return 1 if value <= 10 else 0.75 if 10 < value <= 20 else 0.5 if 20 < value <= 35 else 0.25 if 35 < value <= 50 else 0


def get_nm_weight(value):
    return 1 if value <= 7 else 0.75 if 7 < value <= 10 else 0.5 if 10 < value <= 13 else 0.25 if 13 < value <= 16 else 0


def get_dit_weight(value):
    return 1 if value <= 5 else 0.75 if 5 < value <= 7 else 0.5 if 7 < value <= 9 else 0.25 if 9 < value <= 10 else 0