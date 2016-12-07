from flask import Flask, request, url_for, render_template
from subprocess import call
import sys
sys.path.append("libs");
import worker

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/api/fn')
@app.route('/api/fn/')
@app.route('/api/fn/<fn>', methods=['GET', 'POST'])
def fn(fn=None):
    """ api sample
    <description>
    args:
    returns:
    """
    app.logger.debug('fn name: %s, method is %s' % (fn, request.method))
    return 'fn name: %s, method is %s' % (fn, request.method)

@app.route('/api/get_stock_basics', methods=['GET'])
@app.route('/api/get_stock_basics/', methods=['GET'])
@app.route('/api/get_stock_basics/<code>', methods=['GET'])
def get_stock_basics(code='600000'):
    """ get particular stock basics according to the code
    args: stock code
    returns: a json object string, the basics of the particular stock
    """
    return str(json.loads(worker.get_stock_basics())[code])

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
