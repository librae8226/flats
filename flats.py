import click
import sys
import json
sys.path.append("libs");
import worker

class Config(object):

    def __init(self):
        self.debug = False

pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('--debug', is_flag = True)
@click.option('--path', type = click.Path())
@pass_config
def cli(opt, debug, path):
    ''' This script is built upon worker lib\n
    e.g.\n
    '''
    opt.debug = debug
    if path is None:
        path = '.'
    opt.path = path

@cli.command()
@click.option('--mode', default = 'm', help = 'd/w/m/y: daily, weekly, monthly or yearly')
@click.argument('code', required = True)
@pass_config
def get_basics(opt, mode, code):
    ''' This command get stock basics\n
    '''
    if opt.debug:
        click.echo('opt path: %s' %opt.path)
        click.echo('out: %s' %out)
    print json.loads(worker.get_stock_basics())[code]
    return None

# Below lines are used to run this script directly in python env:
if __name__ == '__main__':
    cli()
