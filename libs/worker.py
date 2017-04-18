import os
import tushare as ts
import pandas as pd
from datetime import datetime
from log import log

PREFIX = 'data'

def get_name_by_code(code):
    q_str = 'code==' + '\"' + code + '\"';
    # FIXME should use the latest report file
    df = pd.read_csv('data/2015q4.csv', dtype={'code': object}).sort_values(by='code').drop_duplicates()
    return df.query(q_str).name.values[0]

def get_est_price(mode, years, code):
    return 1.0, 2.1, 3.2

def get_stock_basics():
    ''' invoke tushare get_stock_basics() with csv output
    args:
    returns: csv format data containing the whole martket information
    json fomat, df.to_json('basics.json', orient='index');
    '''

    filename = PREFIX + '/' + 'basics.csv'
    df = ts.get_stock_basics()
    df.sort_index(inplace=True)
    return df.to_csv(filename, encoding='UTF-8')

def save_to_file(filename, df):
    ''' save df content to file
    args: filename, df
    returns: df
    '''
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=None, encoding='UTF-8', index=False)
    else:
        df.to_csv(filename, encoding='UTF-8', index=False)

    df = pd.read_csv(filename, dtype={'code': object}).sort_values(by='code').drop_duplicates()
    return df.to_csv(filename, encoding='UTF-8', index=False)

def get_report_data(year, quarter):
    ''' invoke tushare get_report_data() with csv output
    brief: to improve data integrality, we repeatedly do these actions in a row,
           call API -> append to file -> drop duplicates
    args: year, quarter
    returns: csv format data containing the whole martket report in specific year, quarter
    json fomat, df.to_json(year+'q'+quarter+'.json', orient='index');
    '''

    # profit
    print "[%s] profit %sq%s" %(datetime.now().strftime("%H:%M:%S.%f"), year, quarter)
    filename = PREFIX + '/' + year + 'q' + quarter + '.profit.csv'
    df = ts.get_profit_data(int(year), int(quarter)).sort_values(by='code').drop_duplicates()
    print "\n"
    save_to_file(filename, df)

    # operation
    print "[%s] operation %sq%s" %(datetime.now().strftime("%H:%M:%S.%f"), year, quarter)
    filename = PREFIX + '/' + year + 'q' + quarter + '.operation.csv'
    df = ts.get_operation_data(int(year), int(quarter)).sort_values(by='code').drop_duplicates()
    print "\n"
    save_to_file(filename, df)

    # growth
    print "[%s] growth %sq%s" %(datetime.now().strftime("%H:%M:%S.%f"), year, quarter)
    filename = PREFIX + '/' + year + 'q' + quarter + '.growth.csv'
    df = ts.get_growth_data(int(year), int(quarter)).sort_values(by='code').drop_duplicates()
    print "\n"
    save_to_file(filename, df)

    # debtpaying
    print "[%s] debtpaying %sq%s" %(datetime.now().strftime("%H:%M:%S.%f"), year, quarter)
    filename = PREFIX + '/' + year + 'q' + quarter + '.debtpaying.csv'
    df = ts.get_debtpaying_data(int(year), int(quarter)).sort_values(by='code').drop_duplicates()
    print "\n"
    save_to_file(filename, df)

    # cashflow
    print "[%s] cashflow %sq%s" %(datetime.now().strftime("%H:%M:%S.%f"), year, quarter)
    filename = PREFIX + '/' + year + 'q' + quarter + '.cashflow.csv'
    df = ts.get_cashflow_data(int(year), int(quarter)).sort_values(by='code').drop_duplicates()
    print "\n"
    save_to_file(filename, df)

    # main report
    print "[%s] main %sq%s" %(datetime.now().strftime("%H:%M:%S.%f"), year, quarter)
    filename = PREFIX + '/' + year + 'q' + quarter + '.csv'
    df = ts.get_report_data(int(year), int(quarter)).sort_values(by='code').drop_duplicates()
    print "\n"
    return save_to_file(filename, df)
