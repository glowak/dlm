import pandas as pd

class CSVInfo:
    '''
    A class representing a .csv document with all the coordination info.
    '''

    def __init__(self, template):
        self.template = template
        self.csv = pd.DataFrame(columns=template.columns)

    def add_info_row(self, info):
        self.csv.loc[len(self.csv)] = info

    def export(self, path):
        self.csv.to_csv(path, index=False)
