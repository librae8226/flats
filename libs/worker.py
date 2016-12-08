import tushare as ts

def get_stock_basics():
    """ invoke tushare get_stock_basics with json object output
    args:
    returns: a json object containing the whole martket information
    """
    return ts.get_stock_basics().to_json('basics.json', orient='index');
    #return ts.get_stock_basics().to_csv('basics.csv', encoding='UTF-8');

def get_report_data(year, quarter):
    """ invoke tushare get_report_data with json object output
    args:
    returns: a json object containing the whole martket report in specific year, quarter
    """
    #return ts.get_report_data(int(year), int(quarter)).to_json(year+'q'+quarter+'.json', orient='index');
    return ts.get_report_data(int(year), int(quarter)).to_csv(year+'q'+quarter+'.csv', encoding='UTF-8',index=False)
