from .model import Session, init_db, File, Round, Player, Solution
from .templates import config_template, render_first, render_second, \
                       render_finished

from datetime import datetime, timedelta, timezone
import os




def init_round(round_num):

    session = Session()
    exists = session.query(Round).filter(Round.id==round_num).one_or_none()
    if exists is not None:
        raise ValueError(round_num)

    if not os.path.exists(str(round_num)):
        os.mkdir(str(round_num))

    if not os.path.exists(f'{round_num}/solutions'):
        os.mkdir(f'{round_num}/solutions')

    session.add(Round(id=round_num))
    session.commit()
    session.close()

    with open(f'{round_num}/config.ini', 'w') as f:
        print(config_template.render(round=round_num), file=f)
    

def start_round(round_num):

    session = Session()
    round = session.query(Round).get(round_num)

    now = datetime.utcnow()

    round.start = now
    round.first_deadline = now + timedelta(days=7)
    session.commit()
    session.close()

    render_first(round_num)


def extend_round(round_number, **delta):

    session = Session()
    round = session.query(Round).get(round_number)

    if round.second_deadline is None:
        round.first_deadline += timedelta(**delta)
        choice = True
    else:
        round.second_deadline += timedelta(**delta)
        choice = False
    session.commit()
    session.close()

    if choice:
        render_first(round_number)
    else:
        render_second(round_number)



def add_player(round, name):

    session = Session()
    others = session.query(Player).filter(Player.round == round).count()
    new_player = Player(id=others + 1, round=round, name=name)
    session.add(new_player)
    session.commit()

    print(f'Created player with id: {new_player.id}')
    
    session.close()


def add_file(round, player_name, name, language='plaintext'):

    session = Session()
    player = session.query(Player).filter(Player.round==round)\
             .filter(Player.name==player_name).one()
    new_file = File(name=name, round=round, player=player.id, language=language)
    session.add(new_file)
    session.commit()
    session.close()


def progress_round(round_num):

    session = Session()
    round = session.query(Round).get(round_num)

    now = datetime.utcnow()

    round.first_deadline = now
    round.second_deadline = now + timedelta(days=7)
    session.commit()
    session.close()

    render_second(round_num)


def solve(round, player_name, solved_name):

    session = Session()
    player = session.query(Player).filter(Player.name==player_name)\
             .filter(Player.round==round).one()
    solved = session.query(Player).filter(Player.name==solved_name)\
             .filter(Player.round==round).one()
    assert solved.id != player.id
    new_solution = Solution(round=round, player=player.id, solved=solved.id)
    session.add(new_solution)
    session.commit()
    session.close()

def close_round(round_num):

    session = Session()
    round = session.query(Round).get(round_num)

    now = datetime.utcnow()

    round.second_deadline = now
    session.commit()
    session.close()

    render_finished(round_num)
