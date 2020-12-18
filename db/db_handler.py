from sqlalchemy import create_engine, MetaData, Table, select, and_
from db.utils import create_user_model, create_meeting_model
from settings import DB_URL

db_engine = create_engine(DB_URL)
conn = db_engine.connect()
metadata = MetaData()
metadata.reflect(bind=db_engine)

users_table = metadata.tables['users']
meetings_table = metadata.tables['meetings']


def build_user_select_statement(s_filter):
    if 'telegram_id' in s_filter:
        return users_table.select().where(users_table.c.telegram_id == s_filter['telegram_id'])
    elif 'redirect_hash' in s_filter:
        return users_table.select().where(users_table.c.redirect_hash == s_filter['redirect_hash'])


def build_meeting_select_statement(s_filter):
    if 'user_telegram_id' in s_filter and 'name' in s_filter:
        return meetings_table.select().where(and_(
            meetings_table.c.user_telegram_id == s_filter['user_telegram_id'],
            meetings_table.c.name == s_filter['name']))

    elif 'user_telegram_id' in s_filter:
        return meetings_table.select().where(meetings_table.c.user_telegram_id == s_filter['user_telegram_id'])


def get_meetings(s_filter):
    if s_filter is None:
        raise ValueError('Meeting filter cannot be empty')
    else:
        select_st = build_meeting_select_statement(s_filter)
    res = conn.execute(select_st).fetchall()
    return res


def get_meeting(s_filter):
    if s_filter is None:
        raise ValueError('Meeting filter cannot be empty')
    else:
        select_st = build_meeting_select_statement(s_filter)
    res = conn.execute(select_st).fetchone()
    return res


def get_users(s_filter=None):
    if s_filter is None:
        select_st = users_table.select()
    else:
        select_st = build_user_select_statement(s_filter)
    res = conn.execute(select_st).fetchall()
    return res


def get_user(s_filter=None):
    if s_filter is None:
        raise ValueError('User filter cannot be empty')
    select_st = build_user_select_statement(s_filter)
    res = conn.execute(select_st).fetchone()
    return res


def create_user(data):
    user_exists = get_user({'telegram_id': data['telegram_id']}) is not None
    if user_exists:
        return
    user_model = create_user_model(data)
    ins = users_table.insert()
    res = conn.execute(ins, [data])
    return res


def set_access_token(redirect_hash, zoom_access_token):
    if redirect_hash is None or zoom_access_token is None:
        return

    query = users_table.update()\
        .where(users_table.c.redirect_hash == redirect_hash)\
        .values({'zoom_access_token': zoom_access_token})

    return conn.execute(query)


def create_meeting(data):
    meeting_model = create_meeting_model(data)
    ins = meetings_table.insert()
    return conn.execute(ins, [data])


def delete_meeting(data):
    meeting = get_meeting(
        {'user_telegram_id': data['user_telegram_id'], 'name': data['name']})
    if not meeting:
        return
    del_st = meetings_table.delete().where(meetings_table.c.id == meeting.id)
    res = conn.execute(del_st)
    return res
