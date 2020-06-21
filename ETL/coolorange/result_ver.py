from coolorange.tools import *

def twin_t_match(model, data, result, col_names, core_only=False):
    """ calculateif twin_t_match

    Parameters: model (model object) - the prediction model obj
                data (DataFrame) - the data load from ETL methods
                result (dict) - a dictionary of real result,
                                can be extracted from ETL method: extract_missing_result()
                                o/w, need to follow the format {race_id:list/array of first 3 places}
                col_names (array-like) - the column names in order that matches with the model dimension
                core_only (boo) - if we only bet on position (i.e. first 3 places)
                                  optional, default is False, i.e. bet on twin-t, not position

    Returns: (dict) - dictionary contains the match result
    """

    def single_race_twin_t(model, separated, col_names, id_, result, core_only=False):
        """ single race result match with twin-t method
        """
        cal_result = model.predict_proba(separated[id_][col_names].values)[:,1]
        sorted_cal_result = np.argsort(cal_result)[::-1] + 1

        real_result = [int(i) for i in result[id_]]

        core_win = [sorted_cal_result[i] in real_result for i in [0,1,2]]
        rest_win = not bool(len(set(real_result) - set(sorted_cal_result[:8])))

        if core_only:
            return core_win
        else:
            prediction_result = np.array(core_win) * np.array(rest_win)
            return prediction_result

    file_name = data.file_name.unique()[0]
    unique_sheet_name = data.sheet_name.unique()
    separated = {'_'.join(format_date_race(file_name, i)):data[data.sheet_name == i] for i in unique_sheet_name}

    all_prediction_result = {i:single_race_twin_t(model, separated, col_names, i, result, core_only) for i in separated}
    return all_prediction_result
