import tushare as ts

def get_stock_basics():
    """ invoke tushare get_stock_basics with json string output
    args:
    returns: a json string containing the whole martket information
    """
    return ts.get_stock_basics().to_json(orient='index');
