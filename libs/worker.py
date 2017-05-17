import os
import tushare as ts
import pandas as pd
from datetime import datetime
from datetime import timedelta
from log import log
from scipy.stats import norm
import numpy
import math

PREFIX = 'data'

def __estimation_formula_bg_dynamic(growth, eps, pe):
    ''' BG formula, integrate with the normal pe (based on Gaussian Distribution)
	original: (2*growth+8.5)*eps
    '''
    return (2*growth+pe)*eps

def __estimation_formula_pb(bvps, pb):
    ''' normal pb (based on Gaussian Distribution)
	original: bvps*pb
    '''
    return bvps*pb

def __pd_read_basics():
    ''' pd.read_csv, for basics
    '''
    return pd.read_csv(PREFIX+'/'+'basics.csv', dtype={'code': object}).drop_duplicates()

def __pd_read_report(q_stat):
    ''' pd.read_csv, for report
    args: q_stat(e.g. '2015q4.profit' or '2016q4')
    '''
    return pd.read_csv(PREFIX+'/'+q_stat+'.csv', dtype={'code': object}).sort_values(by='code').drop_duplicates()

def __pd_read_today_all():
    ''' pd.read_csv, for today
    '''
    return pd.read_csv(PREFIX+'/'+'today_all.csv', dtype={'code': object}).drop_duplicates()

def __quarter_to_date(quarter):
    y = quarter.split('q')[0]
    q = quarter.split('q')[1]
    tail = ['-03-31', '-03-31', '-06-30', '-09-30', '-12-31']
    end = y + tail[int(q)]
    start = str(int(y)-1) + tail[int(q)]
    return start, end

def __get_pe_and_eps(code, quarter):
    ''' get pe of specific quarter
    args: code, quarter(e.g. 2015q3)
    '''
    r = {}
    np = 0
    y = quarter.split('q')[0]
    q = quarter.split('q')[1]
    q_str = 'code==' + '\"' + code + '\"'

    b = __pd_read_basics()
    totals = b.query(q_str).totals.values[0]
    log.debug('totals: %.2f', totals)
    r[quarter] = __pd_read_report(quarter)

    if (q == '4'):
        if (len(r[quarter].query(q_str)) > 0):
            np = r[quarter].query(q_str).net_profits.values[0]
        else:
            log.warn('no entry in %s', quarter)
            return False, False
    else:
	last_q4 = str(int(y)-1)+'q4'
	last_q = str(int(y)-1)+'q'+q
        r[last_q4] = __pd_read_report(last_q4)
        r[last_q] = __pd_read_report(last_q)
        if ((len(r[quarter].query(q_str)) > 0) & (len(r[last_q4].query(q_str)) > 0) & (len(r[last_q].query(q_str)) > 0)):
            np = r[last_q4].query(q_str).net_profits.values[0] - r[last_q].query(q_str).net_profits.values[0] + r[quarter].query(q_str).net_profits.values[0]
        else:
            log.warn('no entry in %s', quarter)
            return False, False

    eps = np/totals/10000.0
    s, e = __quarter_to_date(quarter)
    k = ts.get_k_data(code, ktype='M', start=s, end=e)
    if (len(k) == 0):
        log.warn('no k data entry in %s', quarter)
        return False, False
    pps = k.loc[k.last_valid_index()].close
    log.debug('%s, price: %.2f', e, pps)
    log.debug('np: %.2f', np)
    log.debug('eps: %.2f', eps)
    pe = round(pps/eps, 2)
    log.debug('pe: %.2f', pe)

    return pe, eps

def __get_growth(code, years):
    g = []
    qs = [4, 3, 2, 1]
    for y in range(datetime.now().year - years, datetime.now().year + 1):
        for q in qs:
	    quarter = str(y)+'q'+str(q)
	    if (os.path.exists(PREFIX+'/'+quarter+'.growth.csv')):
		rg = __pd_read_report(quarter+'.growth')
		q_str = 'code==' + '\"' + code + '\"'
		if (len(rg.query(q_str)) > 0):
                    tmp_g = round(rg.query(q_str).nprg.values[0], 2)
                    if (math.isnan(tmp_g)):
                        tmp_g = 0
		    g.append(tmp_g)
		    log.debug('growth@%s: %.2f%%', quarter, tmp_g)
		    break
    growth = round(numpy.mean(g)/100.0, 2)
    log.info('growth: %.2f %d~%d %s', growth, datetime.now().year - years, datetime.now().year, str(g))
    return growth

def __get_eps(code):
    ''' Deprecated! This eps is not a full fiscal year data!
    '''
    b = __pd_read_basics()
    q_str = 'code==' + '\"' + code + '\"'
    eps = b.query(q_str).esp.values[0]
    log.info('eps: %.2f', eps)
    return eps

def __get_k_data_of_last_trade_day(code):
    d = datetime.now()
    k = None
    while True:
	k = ts.get_k_data(code, ktype='M', start=d.strftime("%Y-%m-%d"), end=d.strftime("%Y-%m-%d"))
        if (len(k) > 0):
            break
        else:
            d = d + timedelta(days = -1)
    return k, d

def __get_est_price_mode_pe(realtime, code, years):

    q_str = 'code==' + '\"' + code + '\"'

    pe_obj = {}
    eps = 0
    for y in range(datetime.now().year - years, datetime.now().year + 1):
        for q in range(1, 5):
	    quarter = str(y)+'q'+str(q)
	    if (os.path.exists(PREFIX+'/'+quarter+'.csv')):
		r = __pd_read_report(quarter)
		if (len(r.query(q_str)) > 0):
		    # save all pe history and latest eps
                    tmp_pe, tmp_eps = __get_pe_and_eps(code, quarter)
                    if (isinstance(tmp_pe, float) & isinstance(tmp_eps, float)):
                        pe_obj[quarter] = tmp_pe
                        eps = tmp_eps
                        log.debug('%s pe: %.2f, eps: %.2f', quarter, pe_obj[quarter], eps)
                    else:
                        log.warn('skip %s', quarter)
                        continue
    #sorted(pe_obj)
    #log.debug(pe_obj)
    arr = pe_obj.values()
    mu, std = norm.fit(arr)

    if (realtime):
	d = datetime.now()
	today = __pd_read_today_all()
	close = round(today.query(q_str).trade.values[0], 2)
    else:
	k, d = __get_k_data_of_last_trade_day(code)
	close = round(k.close.values[0], 2)
    log.info('%s price: %.2f @ pe %.2f', d.strftime("%Y-%m-%d"), close, close/eps)
    log.info('mu, std: %.2f, %.2f', mu, std)

    growth = __get_growth(code, years)

    left = __estimation_formula_bg_dynamic(growth, eps, mu - std)
    centrum = __estimation_formula_bg_dynamic(growth, eps, mu)
    right = __estimation_formula_bg_dynamic(growth, eps, mu + std)
    value = __estimation_formula_bg_dynamic(growth, eps, 8.5)

    log.info('est dynamic: %.2f~%.2f~%.2f', left, centrum, right)
    log.info('est value: %.2f', value)
    log.info('range from left: %.2f%%', (close-left)/left*100.0)
    log.info('position: %.2f%%', (close-left)/(right-left)*100.0)

    return left, centrum, right, value

def __get_pb_and_bvps(code, quarter):
    ''' get pb of spbcific quarter
    args: code, quarter(e.g. 2015q3)
    '''
    r = {}
    bvps = 0
    y = quarter.split('q')[0]
    q = quarter.split('q')[1]
    q_str = 'code==' + '\"' + code + '\"'

    r[quarter] = __pd_read_report(quarter)

    if (len(r[quarter].query(q_str)) > 0):
        bvps = r[quarter].query(q_str).bvps.values[0]
    else:
        log.warn('no entry in %s', quarter)
        return False, False

    s, e = __quarter_to_date(quarter)
    k = ts.get_k_data(code, ktype='M', start=s, end=e)
    if (len(k) == 0):
        log.warn('no k data entry in %s', quarter)
        return False, False
    pps = k.loc[k.last_valid_index()].close
    log.debug('%s, price: %.2f', e, pps)
    log.debug('bvps: %.2f', bvps)
    pb = round(pps/bvps, 2)
    log.debug('pb: %.2f', pb)

    return pb, bvps

def __get_est_price_mode_pb(realtime, code, years):

    q_str = 'code==' + '\"' + code + '\"'

    pb_obj = {}
    bvps = 0
    for y in range(datetime.now().year - years, datetime.now().year + 1):
        for q in range(1, 5):
	    quarter = str(y)+'q'+str(q)
	    if (os.path.exists(PREFIX+'/'+quarter+'.csv')):
		r = __pd_read_report(quarter)
		if (len(r.query(q_str)) > 0):
		    # save all pb history and latest bvps
                    tmp_pb, tmp_bvps = __get_pb_and_bvps(code, quarter)
                    if (isinstance(tmp_pb, float) & isinstance(tmp_bvps, float)):
                        pb_obj[quarter] = tmp_pb
                        bvps = tmp_bvps
                        log.debug('%s pb: %.2f, bvps: %.2f', quarter, pb_obj[quarter], bvps)
                    else:
                        log.warn('skip %s', quarter)
                        continue
    #sorted(pb_obj)
    #log.debug(pb_obj)
    arr = pb_obj.values()
    mu, std = norm.fit(arr)

    if (realtime):
	d = datetime.now()
	today = __pd_read_today_all()
	close = round(today.query(q_str).trade.values[0], 2)
    else:
	k, d = __get_k_data_of_last_trade_day(code)
	close = round(k.close.values[0], 2)
    log.info('%s price: %.2f @ pb %.2f', d.strftime("%Y-%m-%d"), close, close/bvps)
    log.info('mu, std: %.2f, %.2f', mu, std)

    left = __estimation_formula_pb(bvps, mu - std)
    centrum = __estimation_formula_pb(bvps, mu)
    right = __estimation_formula_pb(bvps, mu + std)
    value = __estimation_formula_pb(bvps, 1.0)

    log.info('est dynamic: %.2f~%.2f~%.2f', left, centrum, right)
    log.info('est value: %.2f', value)
    log.info('range from left: %.2f%%', (close-left)/left*100.0)
    log.info('position: %.2f%%', (close-left)/(right-left)*100.0)

    return left, centrum, right, value

def get_name_by_code(code):
    q_str = 'code==' + '\"' + code + '\"'
    # FIXME should use the latest report file
    df = pd.read_csv('data/2015q4.csv', dtype={'code': object}).sort_values(by='code').drop_duplicates()
    df_code = df.query(q_str)
    if (len(df_code) > 0):
        return df_code.name.values[0]
    else:
        return None

def get_est_price(realtime, mode, years, code):
    ''' return left, centrum, right price, to form a range
    '''
    if (mode == 'pe'):
	return __get_est_price_mode_pe(realtime, code, years)
    elif (mode == 'pb'):
	return __get_est_price_mode_pb(realtime, code, years)
    else:
	return 0, 0, 0

def get_stock_basics():
    ''' invoke tushare get_stock_basics() with csv output
    args:
    returns: csv format data containing the whole martket information
    json fomat, df.to_json('basics.json', orient='index')
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
    json fomat, df.to_json(year+'q'+quarter+'.json', orient='index')
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

def get_today_all():
    print "[%s] get_today_all" %(datetime.now().strftime("%H:%M:%S.%f"))
    df = ts.get_today_all()
    filename = PREFIX + '/' + 'today_all.csv'
    os.remove(filename)
    return save_to_file(filename, df)
