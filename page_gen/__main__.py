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

    now = datetime.now(timezone.utc)

    round.start = now
    round.first_deadline = now + timedelta(days=7)
    session.commit()
    session.close()

    render_first(round_num)
