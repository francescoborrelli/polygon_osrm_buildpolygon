#  Copyright (c) 2020. AV Connect Inc.
import os

from config import Config
from data import create_app

app = create_app('config.Config')
#ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
if __name__ == "__main__":
    print(os.environ.get('ROOT'))
    app.run(host='0.0.0.0')

