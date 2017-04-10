import os
import tushare as ts
import pandas as pd

PREFIX = 'data'

def get_stock_basics():
    ''' invoke tushare get_stock_basics() with csv output
    args:
    returns: csv format data containing the whole martket information
    '''
    filename = PREFIX + '/' + 'basics.csv'
    df = ts.get_stock_basics().sort_values(by='code')
    return df.to_csv(filename, encoding='UTF-8');
    #return df.to_json('basics.json', orient='index');

def get_report_data(year, quarter):
    ''' invoke tushare get_report_data() with csv output
    brief: to improve data integrality, we repeatedly do these actions in a row,
           call API -> append to file -> drop duplicates
    args: year, quarter
    returns: csv format data containing the whole martket report in specific year, quarter
    '''
    filename = PREFIX + '/' + year + 'q' + quarter + '.csv'
    df = ts.get_report_data(int(year), int(quarter)).sort_values(by='code').drop_duplicates()
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=None, encoding='UTF-8', index=False)
    else:
        df.to_csv(filename, encoding='UTF-8', index=False)

    df = pd.read_csv(filename, dtype={'code': object}).sort_values(by='code').drop_duplicates()
    return df.to_csv(filename, encoding='UTF-8', index=False)
    #return df.to_json(year+'q'+quarter+'.json', orient='index');
