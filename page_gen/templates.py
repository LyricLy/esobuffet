from .model import Session, File, Round, Player, Solution

from jinja2 import Environment, select_autoescape, FileSystemLoader
from datetime import datetime
import configparser


env = Environment(
    loader=FileSystemLoader('page_gen'),
    autoescape=select_autoescape(),
)


first_template = env.get_template('template_first.html')
second_template = env.get_template('template_second.html')
finished_template = env.get_template('template_finished.html')
config_template = env.get_template('template.ini')




def render_first(round_num):

    session = Session()
    round = session.query(Round).get(round_num)
    session.close()

    config = configparser.ConfigParser()
    config.read(f'{round_num}/config.ini')

    with open(f'{round_num}/index.html', 'w') as f:
        print(first_template.render(config=config['round'],
                                    round=round),
              file=f)


def render_second(round_num):
    pass


def render_finished(round_num):
    pass
