from flask import Flask, request, url_for, render_template
from subprocess import call

app = Flask(__name__)

@app.route('/')
def index():
	    return 'Index Page'

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
	return render_template('hello.html', name=name)

@app.route('/about')
def about():
	return 'The about page'

@app.route('/func/<func>')
def run_func(func):
	return 'func name: %s' % func

@app.route('/select', methods=['GET', 'POST'])
def select():
	print 'select entry'
	if request.method == 'GET':
                print 'calling select.sh'
	else:
		print 'do nothing'
	return 'select process done'

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
