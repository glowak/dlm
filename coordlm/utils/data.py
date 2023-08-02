import pandas as pd
from typing import Optional


class CSVInfo:
    '''
    A class representing a .csv document with all the coordination info.
    '''
    def __init__(self, 
                 template: Optional[pd.DataFrame] = None,
                 cols: Optional[list] = None
        ):
        assert template is not None or cols is not None, "columns or template must be specified"

        if template is not None:
            self.csv = pd.DataFrame(columns=template.columns)
        else:
            self.csv = pd.DataFrame(columns=cols)


    def add_row(self, 
                info: dict) -> None:
        self.csv.loc[len(self.csv)] = info


    def export(self, 
               path: str) -> None:
        self.csv.to_csv(path, index=False)