from .model import Session, File, Round, Player, Solution

from charset_normalizer import from_path
from magic import from_file

from jinja2 import Environment, select_autoescape, FileSystemLoader
from datetime import datetime
import configparser
import re


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

    session = Session()
    round = session.query(Round).get(round_num)

    players_data = session.query(Player).filter(Player.round==round_num)\
                   .order_by(Player.id).all()
    players = []
    for p in players_data:
        files_data = session.query(File).filter(File.round==round_num)\
                     .filter(File.player==p.id).all()
        files = []
        for f in files_data:
            try:
                with open(f'{round_num}/{p.id}_{f.name}', 'r') as fi:
                    contents = fi.read()
            except UnicodeDecodeError:
                contents = str(from_path(f'{round_num}/{p.id}_{f.name}').best())
            details = from_file(f'{round_num}/{p.id}_{f.name}')
            # Stolen from cg source:
            details = re.sub(r"^.+? (?:source|script), |(?<=text) executable", "", details)
            files.append({
                'name': f.name,
                'details': details,
                'length': contents.strip().count('\n') + 1,
                'contents': contents,
                'language': f.language,
            })
        players.append({
            'name': p.name,
            'id': p.id,
            'files' : files,
        })

    session.close()

    config = configparser.ConfigParser()
    config.read(f'{round_num}/config.ini')

    with open(f'{round_num}/index.html', 'w') as f:
        print(second_template.render(config=config['round'],
                                     round=round,
                                     players=players),
              file=f)


def render_finished(round_num):
    pass
