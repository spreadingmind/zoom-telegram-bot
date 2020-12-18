from db.models import User, Meeting


def create_user_model(data):
    try:
        user_model = User(
            telegram_id=data['telegram_id'],
            redirect_hash=data['redirect_hash'],
            telegram_username=data['telegram_username'],
            zoom_access_token=data['zoom_access_token']
        )
        return user_model
    except Exception as e:
        raise ValueError('Invalid User model data', e, data)


def create_meeting_model(data):
    try:
        meeting_model = Meeting(
            user_telegram_id=data['user_telegram_id'],
            name=data['name'],
            link=data['link']
        )
        return meeting_model
    except Exception as e:
        raise ValueError('Invalid Meeting model data', e, data)
