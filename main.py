import threading
from bot import run_bot
from oauth import run_app

if __name__ == '__main__':
    t1 = threading.Thread(target=run_bot)
    t2 = threading.Thread(target=run_app)
    t1.start()
    t2.start()
