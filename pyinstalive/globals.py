from .config import Config
def init():
    global config
    global download
    global comments
    global session
    global args
    config = Config
    download = None
    comments = None
    session = None
    args = None