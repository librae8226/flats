from setuptools import setup

setup(
	name = 'flats',
	version = '0.1',
	py_modules = ['flats'],
	include_package_data = True,
	install_requires = [
		'Click',
	],
	entry_points = '''
		[console_scripts]
		flats = flats:cli
	''',
)
