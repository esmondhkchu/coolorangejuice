import numpy as np
import pandas as pd
import re

def drop_if_whole_na(in_df, how):
    """ drop a pandas dataframe row/col if the whole row/col are na

    Parameters: in_df (DataFrame) - a pandas dataframe
                how (str) - 'row' / 'column'

    Returns: (DataFrame) - a cleaned dataframe
    """
    row_num, col_num = in_df.shape

    if how == 'row':
        final_df = in_df.drop(in_df[in_df.isna().sum(1) == col_num].index)
    elif how == 'column':
        drop_col = in_df.columns[in_df.isna().sum(0) == row_num]
        final_df = in_df[[i for i in list(in_df) if i not in drop_col]]

    return final_df

def transform_str_int(in_str):
    """ transform a str to int
        if cannot, return None
    """
    try:
        return int(in_str)
    except:
        return None

def drop_none(in_list):
    """ drop None values of a list
        if whole list is None
        return a single None type object
    """
    dropped = [i for i in in_list if i is not None]
    if dropped:
        return dropped
    else:
        return None

def encode_result(n, result):
    """ map result to a vector
        if result is empty, return n None in a list

    eg:
    >>> encode_result(6, [3,2,1])
    [3,2,1,0,0,0]
    """
    result_zeros = np.zeros(n)
    if result:
        for i,j in enumerate(result):
            result_zeros[j-1] = i+1
        return result_zeros
    else:
        return [None]*n

def format_to_date(in_str):
    """ process filename format to datetime
        use in extract_missing_result()

    Parameters: in_str (str) - the excel file name

    Returns: year (str), month (str), day (str)
    """
    datetime = pd.to_datetime(in_str[1:-1])
    year = str(datetime.year)
    month = str(datetime.month)
    if len(month) == 1:
        month = '0'+month
    day = str(datetime.day)
    if len(day) == 1:
        day = '0'+day

    return year, month, day

def format_to_race(in_str):
    """ process Race name to single/double digit
        use in extract_missing_result()

    Parameters: in_str (str) - the sheet name

    Return: (str) - the race number
    """
    try:
        return re.findall(r'\([0-9]+\)', in_str)[0][1:-1]
    except:
        print('Error on {}'.format(in_str))
        return None

def subset_df(in_df, cut_col):
    """ subset a dataframe by the univalue of a column
    """
    my_df = in_df.sort_values([cut_col]).reset_index(drop=True)
    ori = my_df[cut_col]
    shifted = my_df[cut_col].shift(1)

    cut_idx = list(ori[ori != shifted].index) + [my_df.shape[0]]
    cut = [my_df.loc[range(cut_idx[i],cut_idx[i+1])] for i in range(len(cut_idx)-1)]
    return cut

def combine_dicts(in_list):
    """ combine dictionaries into one

    Parameters: in_list (tuple/list/array-like) - a list of dictionaries

    Returns: (dict) - the combined dictionaries
    """
    new_dict = dict()
    for i in in_list:
        for j in i:
            new_dict[j] = i[j]

    return new_dict

def unlist(in_list):
    """ unlist a list of list
    """
    return [j for i in in_list for j in i]
<<<<<<< HEAD

def format_date_race(date, race):
    year, month, day = format_to_date(date)
    race = format_to_race(race)
    return [year, month, day, race]
=======
>>>>>>> 910c800abce44000ad1704d1558f68fa4eaccb9e
