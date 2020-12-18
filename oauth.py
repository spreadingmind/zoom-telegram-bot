from urllib import parse
import requests
from flask import Flask, redirect, jsonify, request
import logging
from settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URL
from db.db_handler import get_user, set_access_token
from settings import PORT

ZOOM_OAUTH_AUTHORIZE_API = 'https://zoom.us/oauth/authorize?response_type=code'
ZOOM_TOKEN_API = 'https://zoom.us/oauth/token?grant_type=authorization_code'
TELEGRAM_BOT_LINK = 'https://tx.me/SimpleZoomBot'

logger = logging.getLogger('app_log')

app = Flask(__name__)


def get_zoom_authorize_link(redirect_hash=""):
    url = "{}&client_id={}&redirect_uri={}".format(
        ZOOM_OAUTH_AUTHORIZE_API, CLIENT_ID, REDIRECT_URL
    )
    if redirect_hash != "":
        url = url + '?zoom_bot_unique_hash={}'.format(redirect_hash)
    return url


@app.route('/')
def get_token():
    try:
        if request.args.get('code'):
            code = request.args.get('code')
            zoom_bot_unique_hash = request.args.get('zoom_bot_unique_hash')
            redirect_url = REDIRECT_URL
            url = ZOOM_TOKEN_API + '&code=' + code + '&redirect_uri=' +\
                parse.quote_plus(
                    redirect_url + '?zoom_bot_unique_hash={}'.format(zoom_bot_unique_hash))
            response = requests.post(url=url, auth=(CLIENT_ID, CLIENT_SECRET))
            if response.status_code == 200:
                response_json = response.json()
                bot_user = get_user({'redirect_hash': zoom_bot_unique_hash})
                if bot_user is not None:
                    set_access_token(zoom_bot_unique_hash,
                                     response_json['access_token'])
                    logger.info("Аccess token is set for user")
                else:
                    logger.info("user with hash does not exists: {}".format(
                        zoom_bot_unique_hash))

                return redirect(location=TELEGRAM_BOT_LINK)
            else:
                logger.info("Get auth code response failed")
                logger.info(response.json())
                response = app.response_class(status=500)

                return response
        else:
            logger.info("Redirecting to authorize app")

            return redirect(location=get_zoom_authorize_link())
    except Exception as e:
        logger.error("Something went wrong",  e)
        response = app.response_class(status=500)
        return response


def run_app():
    app.run(host='0.0.0.0', port=PORT)
