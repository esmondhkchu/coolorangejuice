import sys
sys.path.insert(1, '../ETL/')

from tools import *

class ValidateNewData:
    """ validate new data
    """
    def __init__(self, race, include_col, model):
        """ validate new data

        Parameters: race (DataFrame) - the default dataframe from a single Excel sheet
                    include_col (list) - a list of column names to subset excel to make prediction
                    model (object) - a sklearn model object
        """
        self.race = race
        self.include_col = include_col
        self.model = model

        self.cleaned_data = self.race[include_col]

    def return_race_info(self):
        """ return a single str denotes the race information
        """
        race_day = format_to_date(self.race['file_name'].unique()[0])
        race_num = format_to_race(self.race['sheet_name'].unique()[0])
        self.race_info = '/'.join(race_day) + ' Race: ' + race_num
        return self.race_info

    def scale_data(self, scale):
        """ scale model data or not

        Parameters: scale (obj) - a sklearn scale object
        """
        self.cleaned_data = scale.transform(self.cleaned_data)

    def predict(self):
        """ make prediction
        """
        return self.model.predict(self.cleaned_data)

    def predict_proba(self):
        """ make prediction in probability
        """
        self.proba = self.model.predict_proba(self.cleaned_data)[:,1]
        return self.proba

    def rank_proba(self):
        """ rank probability by horse number
        """
        try:
            return np.argsort(self.proba)[::-1]+1
        except:
            self.predict_proba()
            return np.argsort(self.proba)[::-1]+1
