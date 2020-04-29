import os
import re

import numpy as np
import pandas as pd

import datetime
import json

from tools import *
from scraper import *

def load_excel_sheet(data_path, sheet_name, mapper={'編號':'horse_num'}):
    """ load an excel sheet

    Parameters: data_path (str) - the path to the excel file
                sheet_name (str) - the sheet name
                mapper (dict) - the mapper for renaming column, if empty will do nothing
    """
    raw_df = pd.read_excel(data_path, sheet_name=sheet_name)

    # extract result
    result = drop_none([transform_str_int(i) for i in list(raw_df)])

    col_row_idx = raw_df[list(raw_df)[0]].dropna().index[0]
    # reset column name by detecting the first row with int/float/str
    raw_df.columns = raw_df.loc[col_row_idx].values
    raw_df = raw_df.drop(col_row_idx)

    # # drop all
    raw_df = drop_if_whole_na(raw_df, 'row').reset_index(drop=True)

    first_col_det = raw_df[list(raw_df)[0]].values[:,0]

    # index to cut for second half of table
    cut_idx = np.where(np.array([transform_str_int(i) for i in first_col_det]) == None)[0][0]

    # cut the second half
    raw_df = raw_df.iloc[range(cut_idx)]

    # drop NA columns and duplicated column
    raw_df = drop_if_whole_na(raw_df.loc[:,~raw_df.columns.duplicated()], 'column')
    # reset column name
    final_df = raw_df.rename(columns=mapper).sort_values('horse_num').reset_index(drop=True)

    # add result
    final_df['result'] = encode_result(final_df.shape[0], result)

    # add file name
    file_name = re.findall(r'/[\w|-]+.xls', data_path)[0][1:-4]
    final_df['file_name'] = [file_name]*final_df.shape[0]

    # sheet name
    final_df['sheet_name'] = [sheet_name]*final_df.shape[0]

    return final_df

def load_whole_excel(file_path, sheet_hint, mapper={'編號':'horse_num'}, combined=True, verbose=True):
    """ load every sheet in a excel file

    Parameters: file_path (str) - the path to the excel file
                sheet_hint (str) - the hint to eliminate sheet
                                   eg, hint='Race', then sheet name must contain 'Race'
                mapper (dict) - the mapper for renaming column, if empty will do nothing
                                optional, default is {'編號':'horse_num'}
                combined (boo) - if combined, then will combine all sheets
                                 optional, default is True
                verbose (boo) - print message or not
                                optional, default is True

    Returns: (DataFrame) or (list)
    """
    if verbose:
        print('Loading file: {}'.format(file_path))

    all_sheets_name = [i for i in pd.ExcelFile(file_path).sheet_names if sheet_hint in i]

    if all_sheets_name:
        all_sheets = list()
        for i in all_sheets_name:
            try:
                data = load_excel_sheet(file_path, i, mapper)
                all_sheets.append(data)
                if verbose:
                    print('Loaded: {}'.format(i))
            except:
                if verbose:
                    print('Failed to load sheet: {}'.format(i))
        if verbose:
            print('Status: Completed\n')

        if combined:
            return pd.concat(all_sheets, sort=False).reset_index(drop=True)
        else:
            return all_sheets

    else:
        if verbose:
            print('Sheet hint error')
            print('Status: Failed\n')
        return None

def flow_from_dir(path, file_extension, sheet_hint, mapper={'編號':'horse_num'}, combined=True, verbose=True):
    """ load all data with the same file extention from a directory

    Parameters: path (str) - the directory
                file_extension (str) - the file extension
                sheet_hint (str) - the hint to eliminate sheet
                                   eg, hint='Race', then sheet name must contain 'Race'
                mapper (dict) - the mapper for renaming column, if empty will do nothing
                                optional, default is {'編號':'horse_num'}
                combined (boo) - if combined, then will combine all sheets
                                 optional, default is True
                verbose (boo) - print message or not
                                optional, default is True

    Returns: (DataFrame) or (list)
    """
    all_files = [i for i in os.listdir(path) if file_extension in i]

    all_data = list()
    for j,i in enumerate(all_files):
        if verbose:
            print('File {}'.format(j+1))
        data = load_whole_excel(os.path.join(path, i), sheet_hint, mapper, combined, verbose)
        all_data.append(data)

    if verbose:
        print('Loaded {} files'.format(len(all_files)))

    if combined and all_data:
        try:
            return pd.concat(all_data, sort=False).reset_index(drop=True)
        except:
            if verbose:
                print('\nError in loading file\nGlobal issue, check files')
    elif combined is False and all_data:
        return all_data
    else:
        return None

##########- map data from external source -##########

def extract_missing_result(data, browser_path, retry=True, verbose=True, save=True):
    """ load an excel file from load_data module
        and detect which day and race has no result
        then scrape from HKJC to collect the specific data

    Parameters: data (df) - the dataframe load from either load_whole_excel() or flow_from_dir()
                browser_path (str) - the browser path
                retry (boo) - retry failed scraping or not, optional, default is True
                verbose (boo) - print message or not, optinal, default is True
                save (boo) - save result or not, optional, default is True

    Returns: all_collection (dict) - a collection of results
    """
    my_data = data[['result','file_name','sheet_name']]

    # detect which day and race has no result
    date_race = my_data[my_data.result.isna()][['file_name','sheet_name']].drop_duplicates().values

    # store race result
    all_collection = dict()
    # initiate session to extract result
    hkjc = HKJCRaceResult(browser_path)

    # store failed info and retry later
    retry_list = list()

    for i,j in date_race:
        year, month, day = format_to_date(i)
        race_num = format_to_race(j)
        # key name for dictionary
        id_ = '_'.join([year, month, day, race_num])
        try:
            # load that specific page
            hkjc.load_race_source(year, month, day, race_num)
            # overall race result
            result = hkjc.extract_race_result()
            # specific rank
            rank = result[result['Pool'] == 'PLACE']['Winning Combination'].values.tolist()
            # append to dictionary
            all_collection[id_] = rank
            if verbose:
                print('Loaded Result for: {}'.format(id_))
        except:
            retry_list.append((year, month, day, race_num))
            if verbose:
                print('Failed to Load Result for: {}'.format(id_))

    if retry and retry_list:
        for i in retry_list:
            id_ = '_'.join(i)
            if verbose:
                print('Retrying: {}'.format(id_))
            try:
                hkjc.load_race_source(i[0], i[1], i[2], i[3])
                result = hkjc.extract_race_result()
                rank = result[result['Pool'] == 'PLACE']['Winning Combination'].values.tolist()
                all_collection[id_] = rank
                print('Loaded Result for: {}'.format(id_))
            except:
                if verbose:
                    print('Failed to Load Result for: {}'.format(id_))

    hkjc.close_browser()

    if save:
        json_ = json.dumps(all_collection)
        filename = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')+'.txt'
        with open(filename, 'w') as outfile:
            json.dump(all_collection, outfile)

    return all_collection

def map_result_to_day_data(in_day_data, in_result, return_type='dataframe'):
    """ map an external extracted result to data
        serve as a supportive function to map_result_to_data()

    Parameters: in_day_data (DataFrame) - a single day (multiple races) race data
                                          if using internal code, then the data load from load_whole_excel()
                in_result (dict) - result in a dictionary, format: {id_:[rank1, rank2, rank3], ...}
                                                                   id_ is the project standard id,
                                                                   eg, 10/27/2019 Race 1 -> 2019_10_27_1
                                                                   can be extracted using extract_missing_result()
                                                                   save option is available
                                   if using internal code, then the data load from extract_missing_result()
                return_type (str) - return type, optional, defaul is 'dataframe'
                                    accept values: 'dataframe', 'dict'

    Returns: (dict) - mapped result to the data, format: {id_:df, ...}
    """
    data_dict = dict()
    separated_data = subset_df(in_day_data, 'sheet_name')

    for i in separated_data:
        # mapped id_, eg '2019_10_27_9'
        id_ = '_'.join(format_to_date(i['file_name'].values[0]))+'_'+format_to_race(i['sheet_name'].values[0])
        if id_ in in_result:
            # sort df so to map with result
            sorted_df = i.sort_values('horse_num')
            # result, map it from in_result
            result = encode_result(i.shape[0], [transform_str_int(i) for i in in_result[id_]])
            sorted_df['result'] = result
            sorted_df = sorted_df.reset_index(drop=True)
            data_dict[id_] = sorted_df
        else:
            continue
    if return_type is 'dataframe':
        return pd.concat(data_dict.values()).reset_index(drop=True)
    elif return_type is 'dict':
        return data_dict

def map_result_to_data(in_df, in_result, verbose=True):
    """ map an external extracted result to data (directory or single excel file)

    in_day_data (DataFrame) - a single day (multiple races) race data
                                          if using internal code, then the data load from load_whole_excel()
                in_result (dict) - result in a dictionary, format: {id_:[rank1, rank2, rank3], ...}
                                                                    id_ is the project standard id,
                                                                    eg, 10/27/2019 Race 1 -> 2019_10_27_1
                                                                    can be extracted using extract_missing_result()
                                                                    save option is available
                                   if using internal code, then the data load from extract_missing_result()
               verbose (boo) - print error message or not, optional, default is True

    """
    subset = subset_df(in_df, 'file_name')
    all_data = list()
    for i in subset:
        try:
            appended = map_result_to_day_data(i, in_result)
            all_data.append(appended)
        except:
            day = '_'.join(format_to_date(i['file_name'].values[0]))
            if verbose:
                print('Race day {} has no result'.format(day))
            continue

    overall = pd.concat(all_data).reset_index(drop=True)
    return overall
