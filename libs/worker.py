import os
import tushare as ts
import pandas as pd
from datetime import datetime
from log import log
from scipy.stats import norm

PREFIX = 'data'

def __estimation_formula_bg_dynamic(growth, eps, pe):
    ''' BG formula, integrate with the normal pe (based on Gaussian Distribution)
	original: (2*growth+8.5)*eps
    '''
    return (2*growth+pe)*eps

def __pd_read_basics():
    ''' pd.read_csv, for report
    args: q_stat(e.g. '2015q4.profit' or '2016q4')
    '''
    return pd.read_csv(PREFIX+'/'+'basics.csv', dtype={'code': object}).drop_duplicates()

def __pd_read_report(q_stat):
    ''' pd.read_csv, for report
    args: q_stat(e.g. '2015q4.profit' or '2016q4')
    '''
    return pd.read_csv(PREFIX+'/'+q_stat+'.csv', dtype={'code': object}).sort_values(by='code').drop_duplicates()

def __quarter_to_date(quarter):
    y = quarter.split('q')[0]
    q = quarter.split('q')[1]
    tail = ['-03-31', '-03-31', '-06-30', '-09-30', '-12-31']
    end = y + tail[int(q)]
    start = str(int(y)-1) + tail[int(q)]
    return start, end

def __get_pe(code, quarter):
    ''' get pe of specific quarter
    args: code, quarter(e.g. 2015q3)
    '''
    r = {}
    np = 0
    y = quarter.split('q')[0]
    q = quarter.split('q')[1]
    q_str = 'code==' + '\"' + code + '\"';

    b = __pd_read_basics()
    totals = b.query(q_str).totals.values[0]
    log.debug('totals: %.2f', totals)
    r[quarter] = __pd_read_report(quarter);

    if (q == '4'):
        np = r[quarter].query(q_str).net_profits.values[0]
    else:
	last_q4 = str(int(y)-1)+'q4'
	last_q = str(int(y)-1)+'q'+q
        r[last_q4] = __pd_read_report(last_q4);
        r[last_q] = __pd_read_report(last_q);
        np = r[last_q4].query(q_str).net_profits.values[0] - r[last_q].query(q_str).net_profits.values[0] + r[quarter].query(q_str).net_profits.values[0]

    eps = np/totals/10000.0
    s, e = __quarter_to_date(quarter)
    k = ts.get_k_data(code, ktype='M', start=s, end=e)
    pps = k.loc[k.last_valid_index()].close
    log.debug('%s~%s, pps: %.2f', s, e, pps)
    log.debug('eps: %.2f', eps)
    pe = round(pps/eps, 2)
    log.debug('pe: %.2f', pe)

    return pe

def __get_est_price_mode_pe(years, code):
    pe_obj = {}
    for y in range(datetime.now().year - years, datetime.now().year + 1):
        for q in range(1, 5):
	    quarter = str(y)+'q'+str(q)
	    if (os.path.exists(PREFIX+'/'+quarter+'.csv')):
		r = __pd_read_report(quarter);
		q_str = 'code==' + '\"' + code + '\"';
		if (len(r.query(q_str)) > 0):
		    pe_obj[quarter] = __get_pe(code, quarter)
		    log.info('%s: %.2f', quarter, pe_obj[quarter])
    #sorted(pe_obj)
    #log.debug(pe_obj)
    arr = pe_obj.values()
    mu, std = norm.fit(arr)
    log.info('%.2f~%.2f~%.2f', mu - std, mu, mu + std)
    return 1.0, 2.1, 3.2

def get_name_by_code(code):
    q_str = 'code==' + '\"' + code + '\"';
    # FIXME should use the latest report file
    df = pd.read_csv('data/2015q4.csv', dtype={'code': object}).sort_values(by='code').drop_duplicates()
    return df.query(q_str).name.values[0]

def get_est_price(mode, years, code):
    ''' return left, centrum, right price, to form a range
    '''
    if (mode == 'pe'):
	return __get_est_price_mode_pe(years, code)
    else:
	return 0, 0, 0

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
