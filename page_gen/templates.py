from .model import Session, File, Round, Player, Solution

from jinja2 import Environment, select_autoescape, FileSystemLoader
from sqlalchemy.orm import aliased
from sqlalchemy import and_, func
from charset_normalizer import from_path
from magic import from_file

from datetime import datetime
from math import lcm
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


def render_stage(round_num, template):

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
            'solved_by' : 0,
            'score' : 0,
        })

    solve_alias = aliased(Player, name='solve_alias')
    solve_data = session.query(Player, solve_alias).select_from(Player)\
                 .join(Solution, and_(Solution.player==Player.id,
                                      Solution.round==Player.round))\
                 .join(solve_alias, and_(solve_alias.id==Solution.solved,
                                         solve_alias.round==Solution.round))\
                 .filter(Solution.round==round_num)\
                 .order_by(Player.id, solve_alias.id).all()

    for _, p in solve_data:
        players[p.id - 1]['solved_by'] += 1
    multiplier = lcm(*(p['solved_by'] for p in players if p['solved_by'] > 0))
    for who, whom in solve_data:
        players[who.id-1]['score'] += multiplier//players[whom.id-1]['solved_by']
    for player in players:
        player['score'] += multiplier//player['solved_by']\
                           if player['solved_by'] > 0 else 0
    for player in players:
        player['place'] = sum(p['score'] > player['score'] for p in players) + 1

    session.close()

    config = configparser.ConfigParser()
    config.read(f'{round_num}/config.ini')

    with open(f'{round_num}/index.html', 'w') as f:
        print(template.render(config=config['round'],
                              round=round,
                              players=players,
                              solve_data=solve_data,
                              multiplier=multiplier),
              file=f)


render_first = lambda x: render_stage(x, first_template)
render_second = lambda x: render_stage(x, second_template)
render_finished = lambda x: render_stage(x, finished_template)
