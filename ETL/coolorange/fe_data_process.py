import numpy as np
import pandas as pd

def subset_df(in_df, cut_col):
    """ subset a dataframe by the univalue of a column
    """
    my_df = in_df.sort_values([cut_col]).reset_index(drop=True)
    ori = my_df[cut_col]
    shifted = my_df[cut_col].shift(1)

    cut_idx = list(ori[ori != shifted].index) + [my_df.shape[0]]
    cut = [my_df.loc[range(cut_idx[i],cut_idx[i+1])] for i in range(len(cut_idx)-1)]
    return cut

def pad_df(in_df, sort_values, pad_target=14):
    """ pad a dataframe to a pad target
    """
    my_df = in_df.reset_index(drop=True)

    check_type = pd.Series([isinstance(i, float) for i in my_df[sort_values]])
    sorted_ = my_df.loc[check_type].sort_values(sort_values, ascending=False)

    pad_items = {
                'horse_num':range(in_df.shape[0]+1, pad_target+1),
                'sheet_name':[in_df['sheet_name'].values[0]]*(pad_target-in_df.shape[0]),
                'Probability':['Nan']*(pad_target-in_df.shape[0])
                }

    return pd.concat([sorted_, my_df[~check_type], pd.DataFrame(pad_items)]).reset_index(drop=True)

def rename_column_drop_one(in_df, name_col):
    """ rename columns by appending the name of the dropped column
    """
    name = in_df[name_col][0]
    new_name = '{} {}'.format(name_col, name)
    return in_df.rename(columns={i:'{} {}'.format(i, name) for i in list(in_df)}).drop(columns=new_name)

def to_str_percent(in_float, digit):
    """ change a float to percentage
    """
    if isinstance(in_float, (int, float)):
        cleaned = round(in_float*100, digit)
        return '{}%'.format(cleaned)
    else:
        return in_float
