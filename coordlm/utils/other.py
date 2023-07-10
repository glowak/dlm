import pandas as pd
from trankit import trankit2conllu

def load_data(corpus):
    with open(corpus, "r") as file:
        document = file.readlines()
    return document


def create_csv_template(columns_info_path):
    template = pd.read_csv(columns_info_path)
    return template


def toconllu(parsed_data, filename):
    conllu_doc = trankit2conllu(parsed_data)
    with open(filename, "w") as file:
        file.write(conllu_doc)