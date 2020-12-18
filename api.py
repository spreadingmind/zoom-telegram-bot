import requests
import logging


logger = logging.getLogger('app_log')
BASE_URL = 'https://api.zoom.us/v2/users/'


def get_my_zoom_info(token):
    url = BASE_URL + 'me'
    headers = {
        'Authorization': 'Bearer ' + token
    }
    try:
        response = requests.get(url=url, headers=headers)
        return response.json()
    except Exception as e:
        logger.error("Error in getting user info", e)


def get_user_meetings(token, user_id):
    url = BASE_URL + user_id + '/meetings'
    headers = {
        'Authorization': 'Bearer ' + token
    }
    try:
        response = requests.get(url=url, headers=headers)
        return response.json()
    except Exception as e:
        logger.error("Error in getting user meetings", e)


def create_zoom_meeting(token, user_id):
    url = BASE_URL + user_id + '/meetings'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url=url, headers=headers, json={})
        return response.json()
    except Exception as e:
        logger.error("Error in getting user meetings", e)
        return None