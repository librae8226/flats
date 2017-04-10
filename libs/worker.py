import os
import tushare as ts
import pandas as pd

def get_stock_basics():
    ''' invoke tushare get_stock_basics with json object output
    args:
    returns: a json object containing the whole martket information
    '''
    df = ts.get_stock_basics().sort_values(by='code')
    return df.to_json('basics.json', orient='index');
    #return df.to_csv('basics.csv', encoding='UTF-8');

def get_report_data(year, quarter):
    ''' invoke tushare get_report_data with json object output
    brief: to improve data integrality, we repeatedly do these actions in a row,
           call API -> append to file -> drop duplicates
    args: year, quarter
    returns: a json object containing the whole martket report in specific year, quarter
    '''
    df = ts.get_report_data(int(year), int(quarter)).sort_values(by='code').drop_duplicates()
    if os.path.exists(year+'q'+quarter+'.csv'):
        df.to_csv(year+'q'+quarter+'.csv', mode='a', header=None, encoding='UTF-8', index=False)
    else:
        df.to_csv(year+'q'+quarter+'.csv', encoding='UTF-8', index=False)

    df = pd.read_csv(year+'q'+quarter+'.csv', dtype={'code': object}).sort_values(by='code').drop_duplicates()
    return df.to_csv(year+'q'+quarter+'.csv', encoding='UTF-8', index=False)
    #return df.to_json(year+'q'+quarter+'.json', orient='index');
